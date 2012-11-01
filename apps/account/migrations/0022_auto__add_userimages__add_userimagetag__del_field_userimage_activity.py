# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'UserImages'
        db.create_table('account_userimages', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('image', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['account.UserImage'])),
            ('profile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['account.UserProfile'])),
            ('activity', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('account', ['UserImages'])

        # Adding model 'UserImageTag'
        db.create_table('account_userimagetag', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('image', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['account.UserImage'])),
            ('profile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['account.UserProfile'], null=True, blank=True)),
            ('page', self.gf('django.db.models.fields.CharField')(max_length='100', null=True, blank=True)),
            ('coords', self.gf('account.models.CoordsField')()),
            ('is_delete', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('account', ['UserImageTag'])

        # Deleting field 'UserImage.activity'
        db.delete_column('account_userimage', 'activity')

        # Removing M2M table for field profiles on 'UserImage'
        db.delete_table('account_userimage_profiles')


    def backwards(self, orm):
        # Deleting model 'UserImages'
        db.delete_table('account_userimages')

        # Deleting model 'UserImageTag'
        db.delete_table('account_userimagetag')

        # Adding field 'UserImage.activity'
        db.add_column('account_userimage', 'activity',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding M2M table for field profiles on 'UserImage'
        db.create_table('account_userimage_profiles', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('userimage', models.ForeignKey(orm['account.userimage'], null=False)),
            ('userprofile', models.ForeignKey(orm['account.userprofile'], null=False))
        ))
        db.create_unique('account_userimage_profiles', ['userimage_id', 'userprofile_id'])


    models = {
        'account.friendrequest': {
            'Meta': {'unique_together': "(('from_user', 'to_user'),)", 'object_name': 'FriendRequest'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'from_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'from_user'", 'to': "orm['account.UserProfile']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'to_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'to_user'", 'to': "orm['account.UserProfile']"})
        },
        'account.relationship': {
            'Meta': {'object_name': 'Relationship'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'from_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'from_people'", 'to': "orm['account.UserProfile']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': '1', 'max_length': "'1'"}),
            'to_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'to_people'", 'to': "orm['account.UserProfile']"})
        },
        'account.userimage': {
            'Meta': {'object_name': 'UserImage'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'my_images'", 'to': "orm['account.UserProfile']"}),
            'profiles': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'all_images'", 'symmetrical': 'False', 'through': "orm['account.UserImages']", 'to': "orm['account.UserProfile']"}),
            'rating': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        'account.userimages': {
            'Meta': {'object_name': 'UserImages'},
            'activity': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['account.UserImage']"}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['account.UserProfile']"})
        },
        'account.userimagetag': {
            'Meta': {'object_name': 'UserImageTag'},
            'coords': ('account.models.CoordsField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['account.UserImage']"}),
            'is_delete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'page': ('django.db.models.fields.CharField', [], {'max_length': "'100'", 'null': 'True', 'blank': 'True'}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['account.UserProfile']", 'null': 'True', 'blank': 'True'})
        },
        'account.useroptions': {
            'Meta': {'object_name': 'UserOptions'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': "'100'"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['account.UserProfile']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': "'100'"})
        },
        'account.userprofile': {
            'Meta': {'object_name': 'UserProfile', '_ormbases': ['auth.User']},
            'blocked': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'blocked_from'", 'symmetrical': 'False', 'to': "orm['account.UserProfile']"}),
            'filters': ('django.db.models.fields.CharField', [], {'default': "'F'", 'max_length': "'10'"}),
            'followers': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'following'", 'symmetrical': 'False', 'through': "orm['account.Relationship']", 'to': "orm['account.UserProfile']"}),
            'friends': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'friends_rel_+'", 'to': "orm['account.UserProfile']"}),
            'hidden': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'hidden_from'", 'symmetrical': 'False', 'to': "orm['account.UserProfile']"}),
            'optional_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': "'200'"}),
            'photo': ('django.db.models.fields.files.ImageField', [], {'default': "'images/noProfilePhoto.png'", 'max_length': '100'}),
            'user_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True', 'primary_key': 'True'})
        },
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['account']