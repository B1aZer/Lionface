from django.db import models
from account.models import UserProfile
from django.db.models.signals import m2m_changed
from django.db.models.query import Q
import cPickle
import re
import logging

# Create your models here.

class Degree(models.Model):
    from_user = models.ForeignKey(UserProfile, related_name='degree_from')
    to_user = models.ForeignKey(UserProfile, related_name='degree_to')
    date = models.DateTimeField(auto_now_add=True)
    distance = models.IntegerField(default=0)
    path = models.TextField(blank=True)

    def get_length(self):
        length = self.distance
        length_from_path = len(self.path.split(',')) - 2

        if length != length_from_path:
            logger = logging.getLogger(__name__)
            logger.error('error in dos fields')
            raise Exception('wrong field for degrees (OS)');
        return length_from_path

def create_degree_of_separation(sender, instance, action, reverse, model, pk_set, using, **kwargs):

    def _remove_connection(user, friend):
        """
        remove current
        update dependants
        """
        # stat
        removed_count = 0
        updated_count = 0
        dep_count = 0
        # global flags
        updating = False
        updating_rev = False
        # conn's without shortest paths
        deps_lost = []
        deps_rev_lost = []
        # current
        current = Degree.objects.filter(from_user=user, to_user=friend)
        current_rev = Degree.objects.filter(to_user=user, from_user=friend)
        current.delete()
        current_rev.delete()

        # find all dependants
        #deps = Degree.objects.extra(where=["path like '%%"+str(user.id)+"%%"+str(friend.id)+"%%'"]).order_by('distance')
        #deps_rev = Degree.objects.extra(where=["path like '%%"+str(friend.id)+"%%"+str(user.id)+"%%'"]).order_by('distance')
        deps = Degree.objects.filter(path__contains='%s,%s' % (user.id, friend.id))
        deps_rev = Degree.objects.filter(path__contains='%s,%s' % (friend.id, user.id))

        if deps.count():
            updating = True
            dep_count += deps.count()
        if deps_rev.count():
            updating_rev = True
            dep_count += deps_rev.count()

        """
        logic here:
            ask all nighbours if they have path to old node
            if yes, update
            we need 2 loops
            1st one for finding new shrtest
            2nd one for updating othe cells

            or go system

            while loop
            check all friends, on ckecking mark checked
            remove from queue on 0 friends left
            should run 2 times (?)
        """
        deps = list(deps)
        deps_lost = list(deps)
        while updating:
            # flag for global update
            # we need to run all dependants at least once
            updating = False
            for dep in deps:
                #deps.remove(dep)
                neighs = Degree.objects.filter(from_user=dep.from_user, distance = 0)
                for neigh in neighs:
                    try:
                        shortest = Degree.objects.get(from_user=neigh.to_user, to_user=dep.to_user)
                        # hooray! shortest pass
                        if '%s,%s' % (user.id, friend.id) not in shortest.path:
                            # check length (and current path)
                            if '%s,%s' % (user.id, friend.id) in dep.path:
                                # if we have wrong path
                                dep.path = "%s,%s" % (dep.from_user.id, shortest.path)
                                dep.distance = shortest.distance + 1
                                dep.save()
                                deps_lost.remove(dep)
                                updating = True
                            else:
                                # path already updated from neighbour
                                # we need to check current length
                                if shortest.distance + 1 < dep.distance:
                                    dep.path = "%s,%s" % (dep.from_user.id, shortest.path)
                                    dep.distance = shortest.distance + 1
                                    dep.save()
                                    updating = True
                    except Degree.DoesNotExist:
                        continue
                # if no shortest found
                # append to lost list
                #if not updated:
                    #deps_lost.append(dep)

        deps_rev = list(deps_rev)
        deps_rev_lost = list(deps_rev)
        while updating_rev:
            updating_rev = False
            for dep in deps_rev:
                #deps_rev.remove(dep)
                neighs = Degree.objects.filter(from_user=dep.from_user, distance = 0)
                for neigh in neighs:
                    try:
                        shortest = Degree.objects.get(from_user=neigh.to_user, to_user=dep.to_user)
                        if '%s,%s' % (friend.id, user.id) not in shortest.path:
                            if '%s,%s' % (friend.id, user.id) in dep.path:
                                dep.path = "%s,%s" % (dep.from_user.id, shortest.path)
                                dep.distance = shortest.distance + 1
                                dep.save()
                                updated_count += 1
                                updating_rev = True
                                deps_rev_lost.remove(dep)
                            else:
                                if shortest.distance + 1 < dep.distance:
                                    dep.path = "%s,%s" % (dep.from_user.id, shortest.path)
                                    dep.distance = shortest.distance + 1
                                    dep.save()
                                    updated_count += 1
                                    updating_rev = True
                    except Degree.DoesNotExist:
                        continue

        if deps_lost:
            # remove all connections
            removed_count += len(deps_lost)
            for conn in deps_lost:
                conn.delete()
        else:
            # restre original
            neighs = Degree.objects.filter(from_user=user, distance = 0)
            for neigh in neighs:
                try:
                    shortest = Degree.objects.get(from_user=neigh.to_user, to_user=friend)
                    if '%s,%s' % (user.id, friend.id) not in shortest.path:
                        obj, created = Degree.objects.get_or_create(from_user=user, to_user=friend)
                        if created:
                            obj.path="%s,%s" % (user.id, shortest.path)
                            obj.distance = shortest.distance + 1
                            obj.save()
                        else:
                            if shortest.distance + 1 < obj.distance:
                                obj.path="%s,%s" % (user.id, shortest.path)
                                obj.distance = shortest.distance + 1
                                obj.save()
                except Degree.DoesNotExist:
                    continue

        if deps_rev_lost:
            removed_count += len(deps_rev_lost)
            for conn in deps_rev_lost:
                conn.delete()
        else:
            neighs = Degree.objects.filter(from_user=friend, distance = 0)
            for neigh in neighs:
                try:
                    shortest = Degree.objects.get(from_user=neigh.to_user, to_user=user)
                    if '%s,%s' % (friend.id, user.id) not in shortest.path:
                        obj, created = Degree.objects.get_or_create(from_user=friend, to_user=user)
                        if created:
                            obj.path="%s,%s" % (friend.id, shortest.path)
                            obj.distance = shortest.distance + 1
                            obj.save()
                        else:
                             if shortest.distance + 1 < obj.distance:
                                obj.path="%s,%s" % (friend.id, shortest.path)
                                obj.distance = shortest.distance + 1
                                obj.save()

                except Degree.DoesNotExist:
                    continue

        logger = logging.getLogger(__name__)
        logger.warning('We removed: %s records, updated: %s, dependants: %s/2 ' % (removed_count, updated_count, dep_count))

        return True

    def _make_connection(user, friend, update=False):
        """
        This function will find all dependent cells,
        make new connections
        or update old paths, if necessary
        """
        created = 0
        updated_count = 0
        updated = []
        #import pdb;pdb.set_trace()

        # if we have other connections here:
        conns_inst_to = Degree.objects.filter(to_user=user)
        conns_inst_from = Degree.objects.filter(from_user=user)
        conns_frnd_to = Degree.objects.filter(to_user=friend)
        conns_frnd_from = Degree.objects.filter(from_user=friend)
        #caching results
        pickle_str = cPickle.dumps(conns_inst_to)
        qs1 = cPickle.loads(pickle_str)
        pickle_str = cPickle.dumps(conns_inst_from)
        qs2 = cPickle.loads(pickle_str)
        pickle_str = cPickle.dumps(conns_frnd_to)
        qs3 = cPickle.loads(pickle_str)
        pickle_str = cPickle.dumps(conns_frnd_from)
        qs4 = cPickle.loads(pickle_str)
        # original connection between 2 nodes
        conn, created_conn = Degree.objects.get_or_create(from_user=user, to_user=friend)
        conn.path = "%s,%s" % (user.id, friend.id)
        if not created_conn:
            conn.distance = 0
            update = True
            if {'user':user,'friend':friend} not in updated:
                updated.append({'user':user,'friend':friend})
        # 2 way connection
        reverse_conn, created_reverse_conn = Degree.objects.get_or_create(from_user=friend, to_user=user)
        reverse_conn.path = "%s,%s" % (friend.id, user.id)
        if not created_reverse_conn:
            reverse_conn.distance = 0
            update = True
            if {'user':user,'friend':friend} not in updated:
                updated.append({'user':user,'friend':friend})

        # saving
        conn.save()
        reverse_conn.save()


        if update:
            while updated:
                """
                OPTIMIZE:
                    maybe we could check only half of neighbours
                    since we adding reverse connections to updated list
                    this is not necessary
                logic here:
                #check all neighbours
                #new shortest path ?
                #yes->update check again
                """
            #wile looop
                #import pdb;pdb.set_trace()
                updating = updated.pop()
                user = updating.get('user')
                friend = updating.get('friend')
                current = Degree.objects.get(from_user=user, to_user=friend)
                current_rev = Degree.objects.get(from_user=friend, to_user=user)

                neigh_inst_from = Degree.objects.filter(from_user=user, distance=0)
                # find all connections from my neighbours to newly friend
                # if distance > 1, fix
                if neigh_inst_from.count() > 0:
                    for neigh in neigh_inst_from:
                        try:
                            conn_neigh = Degree.objects.get(to_user=friend, from_user=neigh.to_user)
                            # if distance greater than current + 1
                            if conn_neigh.distance > current.distance + 1:
                                conn_neigh.distance = current.distance + 1
                                # path should be traversed through user
                                #conn_neigh.path = "%s,%s,%s" % (neigh.to_user.id, user.id, friend.id)
                                conn_neigh.path = "%s,%s" % (neigh.to_user.id, current.path)
                                conn_neigh.save()
                                # adding to queue current pair
                                if {'user':neigh.to_user,'friend':friend} not in updated:
                                    updated.append({'user':neigh.to_user,'friend':friend})
                                updated_count += 1
                        except Degree.DoesNotExist:
                            continue
                        # since there can be new connection

                neigh_inst_to = Degree.objects.filter(to_user=user, distance=0)
                if neigh_inst_to.count() > 0:
                    for neigh in neigh_inst_to:
                        try:
                            conn_neigh = Degree.objects.get(to_user=neigh.from_user, from_user=friend)
                            if conn_neigh.distance > current_rev.distance + 1:
                                conn_neigh.distance = current_rev.distance + 1
                                #conn_neigh.path = "%s,%s,%s" % (friend.id, user.id, neigh.from_user.id)
                                conn_neigh.path = "%s,%s" % (current_rev.path, neigh.from_user.id)
                                conn_neigh.save()
                                if {'user':friend,'friend':neigh.from_user} not in updated:
                                    updated.append({'user':friend,'friend':neigh.from_user})
                                updated_count += 1
                        except Degree.DoesNotExist:
                            continue

                # This will fire on reverse connections

                neigh_friend_from = Degree.objects.filter(from_user=friend, distance=0)
                if neigh_friend_from.count() > 0:
                    for neigh in neigh_friend_from:
                        try:
                            conn_neigh = Degree.objects.get(to_user=user, from_user=neigh.to_user)
                            if conn_neigh.distance > current_rev.distance + 1:
                                conn_neigh.distance = current_rev.distance + 1
                                #conn_neigh.path = "%s,%s,%s" % (neigh.to_user.id, friend.id, user.id)
                                conn_neigh.path = "%s,%s" % (neigh.to_user.id, current_rev.path)
                                conn_neigh.save()
                                if {'user':neigh.to_user,'friend':user} not in updated:
                                    updated.append({'user':neigh.to_user,'friend':user})
                                updated_count += 1
                        except Degree.DoesNotExist:
                            continue

                neigh_friend_to = Degree.objects.filter(to_user=friend, distance=0)
                if neigh_friend_to.count() > 0:
                    for neigh in neigh_friend_to:
                        try:
                            conn_neigh = Degree.objects.get(to_user=neigh.from_user, from_user=user)
                            if conn_neigh.distance > current.distance + 1:
                                conn_neigh.distance = current.distance + 1
                                #conn_neigh.path = "%s,%s,%s" % (user.id, friend.id, neigh.from_user.id)
                                conn_neigh.path = "%s,%s" % (current.path, neigh.from_user.id)
                                conn_neigh.save()
                                if {'user':user,'friend':neigh.from_user} not in updated:
                                    updated.append({'user':user,'friend':neigh.from_user})
                                updated_count += 1
                        except Degree.DoesNotExist:
                            continue

            logger = logging.getLogger(__name__)
            logger.warning('We updated: %s records, total: %s users' % (updated_count, UserProfile.objects.count()))


            #!!! This implementation will not work on ALL dependants,
            # since not all dependats have paths traversing through current nodes


            # find all dependent nodes
            # dependent means current nodes, should be in their paths
            # since we have problems with sqlite, we will use where
            """
            dependants = Degree.objects.extra(where=["path like '%%"+str(friend.id)+"%%"+str(user.id)+"%%'"])
            dependants_reverse = Degree.objects.extra(where=["path like '%%"+str(user.id)+"%%"+str(friend.id)+"%%'"])
            dependant = dependants.count() + dependants_reverse.count()
            if dependant:
                for dep in dependants:
                    dep.path = re.sub(r"(%s)(?:[,0-9])+(%s)" % (friend.id,user.id) ,r"\1,\2", dep.path)
                    dep.distance = len(dep.path.split(',')) - 2
                    dep.save()
                for dep in dependants_reverse:
                    dep.path = re.sub(r"(%s)(?:[,0-9])+(%s)" % (user.id,friend.id) ,r"\1,\2", dep.path)
                    dep.distance = len(dep.path.split(',')) - 2
                    dep.save()

                logger = logging.getLogger(__name__)
                logger.warning('We updated: %s records' % (dependant))
            """
        else:
            # We only creating connections for current user
            # but we also need connections for all neighbours
            if qs1.count() > 0:
                created += qs1.count()
                # we need to create passive connection for every connected user
                for cn in qs1:
                    Degree.objects.get_or_create(from_user=cn.from_user,\
                            to_user=friend,\
                            path="%s,%s" % (cn.path, friend.id),\
                            distance = cn.distance + 1)
                    # we also need conn's for every neighbour of this user
                    for cnn in qs4:
                        Degree.objects.get_or_create(from_user=cn.from_user,\
                            to_user=cnn.to_user,\
                            path="%s,%s" % (cn.path, cnn.path),\
                            distance = cn.distance + 1 + cnn.distance + 1)

            # and reverse
            if qs2.count() > 0:
                created += qs2.count()
                # we need to create passive connection for every connected user
                for cn in qs2:
                    Degree.objects.get_or_create(from_user=friend,\
                            to_user=cn.to_user,\
                            path="%s,%s" % (friend.id, cn.path),\
                            distance = cn.distance + 1)
                    for cnn in qs3:
                        Degree.objects.get_or_create(from_user=cnn.from_user,\
                            to_user=cn.to_user,\
                            path="%s,%s" % (cnn.path, cn.path),\
                            distance = cnn.distance + 1 + cn.distance + 1)

            # if we have other connections here:
            if qs3.count() > 0:
                created += qs3.count()
                # we need to create passive connection for every connected user
                for cn in qs3:
                    Degree.objects.get_or_create(from_user=cn.from_user,\
                            to_user=user,\
                            path="%s,%s" % (cn.path, user.id),\
                            distance = cn.distance + 1)
                    for cnn in qs2:
                        Degree.objects.get_or_create(from_user=cn.from_user,\
                            to_user=cnn.to_user,\
                            path="%s,%s" % (cn.path, cnn.path),\
                            distance = cn.distance + 1 + cnn.distance + 1)
            # we also want to make reverse connection here,
            # since we dont know who is friended by whoom
            if qs4.count() > 0:
                #created += qs4.count() * (qs1.count() + 1) - qs1.count()
                created += qs4.count()
                for cn in qs4:
                    Degree.objects.get_or_create(from_user=user,\
                            to_user=cn.to_user,\
                            path="%s,%s" % (user.id, cn.path),\
                            distance = cn.distance + 1)
                    for cnn in qs1:
                        Degree.objects.get_or_create(from_user=cnn.from_user,\
                            to_user=cn.to_user,\
                            path="%s,%s" % (cnn.path, cn.path),\
                            distance = cnn.distance + 1 + cn.distance + 1)
            # saving later, so we wont able to see new connection above
            # this is not necessary since we caching results above
            # saving above

            logger = logging.getLogger(__name__)
            logger.warning('We created: %s new connections, total: %s users' % (created, UserProfile.objects.count()))

        return True

    if action == 'post_remove':
        try:
            pk = pk_set.pop()
            friend = model.objects.get(id=pk)
            #Degree.objects.filter(Q(from_user=instance, to_user=friend) | Q(from_user=friend, to_user=instance)).delete()
            _remove_connection(instance, friend)
        except:
            pass
    elif action == 'post_add':
        try:
            pk = pk_set.pop()
            friend = model.objects.get(id=pk)
            overall = Degree.objects.filter(Q(from_user=instance, to_user=friend) | Q(from_user=friend, to_user=instance))
            if overall.count() > 0:
                # get length of first one
                # we dont need this check
                # since length of new connection will always be greater
                # but we need to call function, so..
                # sometimes this fires..
                if overall[0].get_length():
                    _make_connection(instance, friend)
            # if no current connections
            if overall.count() == 0:
                # we need to check here if new connection have length less than current
                # creating new
                _make_connection(instance, friend)

        except:
            logger = logging.getLogger(__name__)
            logger.warning('error in dos')
m2m_changed.connect(create_degree_of_separation, sender=UserProfile.friends.through)
