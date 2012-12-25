import os
import errno

from django.conf import settings
from django.core.files import locks
from django.core.files.move import file_move_safe
from django.core.files.storage import FileSystemStorage


def get_thumb_name(path):
    name, ext = os.path.splitext(path)
    return name + '.thumb' + ext


class ImageStorage(FileSystemStorage):
    """
    Create image file and empty thumb file.
    """
    # almost all copyed from FileSystemStorage._save
    def _save(self, name, content):
        full_path = self.path(name)

        # Create any intermediate directories that do not exist.
        # Note that there is a race between os.path.exists and os.makedirs:
        # if os.makedirs fails with EEXIST, the directory was created
        # concurrently, and we can continue normally. Refs #16082.
        directory = os.path.dirname(full_path)
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
            except OSError, e:
                if e.errno != errno.EEXIST:
                    raise
        if not os.path.isdir(directory):
            raise IOError("%s exists and is not a directory." % directory)

        # There's a potential race condition between get_available_name and
        # saving the file; it's possible that two threads might return the
        # same name, at which point all sorts of fun happens. So we need to
        # try to create the file, but if it already exists we have to go back
        # to get_available_name() and try again.

        while True:
            try:
                thumb_created = False
                thumb_name = get_thumb_name(full_path)
                try:
                    fd = os.open(thumb_name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, 'O_BINARY', 0))
                    os.close(fd)
                except OSError, e:
                    if e.errno == errno.EEXIST:
                        # Ooops, the file exists. We need a new file name.
                        name = self.get_available_name(name)
                        full_path = self.path(name)
                        continue
                    else:
                        raise
                else:
                    thumb_created = True

                # This fun binary flag incantation makes os.open throw an
                # OSError if the file already exists before we open it.
                fd = os.open(full_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, 'O_BINARY', 0))
                try:
                    locks.lock(fd, locks.LOCK_EX)
                    for chunk in content.chunks():
                        os.write(fd, chunk)
                finally:
                    locks.unlock(fd)
                    os.close(fd)
            except OSError, e:
                if thumb_created:
                    self.delete(thumb_name)
                if e.errno == errno.EEXIST:
                    # Ooops, the file exists. We need a new file name.
                    name = self.get_available_name(name)
                    full_path = self.path(name)
                else:
                    raise
            else:
                # OK, the file save worked. Break out of the loop.
                break

        if settings.FILE_UPLOAD_PERMISSIONS is not None:
            os.chmod(full_path, settings.FILE_UPLOAD_PERMISSIONS)
            os.chmod(get_thumb_name(full_path), settings.FILE_UPLOAD_PERMISSIONS)

        return name
