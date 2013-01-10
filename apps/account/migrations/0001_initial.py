# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'RelationRequest'
        db.create_table('account_relationrequest', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('from_user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='relation_from', to=orm['account.UserProfile'])),
            ('to_user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='relation_to', to=orm['account.UserProfile'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('type', self.gf('django.db.models.fields.TextField')(max_length='1')),
        ))
        db.send_create_signal('account', ['RelationRequest'])

        # Adding model 'FriendRequest'
        db.create_table('account_friendrequest', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('from_user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='from_user', to=orm['account.UserProfile'])),
            ('to_user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='to_user', to=orm['account.UserProfile'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('message', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('account', ['FriendRequest'])

        # Adding unique constraint on 'FriendRequest', fields ['from_user', 'to_user']
        db.create_unique('account_friendrequest', ['from_user_id', 'to_user_id'])

        # Adding model 'UserProfile'
        db.create_table('account_userprofile', (
            ('user_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True, primary_key=True)),
            ('photo', self.gf('images.fields.ImageWithThumbField')(default='uploads/images/noProfilePhoto.png', max_length=100)),
            ('cover_photo', self.gf('django.db.models.fields.files.ImageField')(default='uploads/images/bg_cover.png', max_length=100)),
            ('images_quote', self.gf('django.db.models.fields.CharField')(default='Whose woods these are I think I know, his house is in the village though.', max_length=70)),
            ('images_quote_author', self.gf('django.db.models.fields.CharField')(default='Robert Frost', max_length=20)),
            ('filters', self.gf('django.db.models.fields.CharField')(default='F', max_length='10')),
            ('optional_name', self.gf('django.db.models.fields.CharField')(default='', max_length='200')),
            ('timezone', self.gf('django.db.models.fields.CharField')(max_length='200', blank=True)),
            ('in_relationship', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['account.UserProfile'], unique=True, null=True, blank=True)),
            ('relationtype', self.gf('django.db.models.fields.CharField')(max_length='1', blank=True)),
            ('bio_text', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('birth_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
        ))
        db.send_create_signal('account', ['UserProfile'])

        # Adding M2M table for field friends on 'UserProfile'
        db.create_table('account_userprofile_friends', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_userprofile', models.ForeignKey(orm['account.userprofile'], null=False)),
            ('to_userprofile', models.ForeignKey(orm['account.userprofile'], null=False))
        ))
        db.create_unique('account_userprofile_friends', ['from_userprofile_id', 'to_userprofile_id'])

        # Adding M2M table for field hidden on 'UserProfile'
        db.create_table('account_userprofile_hidden', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_userprofile', models.ForeignKey(orm['account.userprofile'], null=False)),
            ('to_userprofile', models.ForeignKey(orm['account.userprofile'], null=False))
        ))
        db.create_unique('account_userprofile_hidden', ['from_userprofile_id', 'to_userprofile_id'])

        # Adding M2M table for field blocked on 'UserProfile'
        db.create_table('account_userprofile_blocked', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_userprofile', models.ForeignKey(orm['account.userprofile'], null=False)),
            ('to_userprofile', models.ForeignKey(orm['account.userprofile'], null=False))
        ))
        db.create_unique('account_userprofile_blocked', ['from_userprofile_id', 'to_userprofile_id'])

        # Adding model 'Relationship'
        db.create_table('account_relationship', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('from_user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='from_people', to=orm['account.UserProfile'])),
            ('to_user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='to_people', to=orm['account.UserProfile'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default=1, max_length='1')),
        ))
        db.send_create_signal('account', ['Relationship'])

        # Adding model 'UserOptions'
        db.create_table('account_useroptions', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length='100')),
            ('value', self.gf('django.db.models.fields.CharField')(max_length='100')),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['account.UserProfile'])),
        ))
        db.send_create_signal('account', ['UserOptions'])


    def backwards(self, orm):
        # Removing unique constraint on 'FriendRequest', fields ['from_user', 'to_user']
        db.delete_unique('account_friendrequest', ['from_user_id', 'to_user_id'])

        # Deleting model 'RelationRequest'
        db.delete_table('account_relationrequest')

        # Deleting model 'FriendRequest'
        db.delete_table('account_friendrequest')

        # Deleting model 'UserProfile'
        db.delete_table('account_userprofile')

        # Removing M2M table for field friends on 'UserProfile'
        db.delete_table('account_userprofile_friends')

        # Removing M2M table for field hidden on 'UserProfile'
        db.delete_table('account_userprofile_hidden')

        # Removing M2M table for field blocked on 'UserProfile'
        db.delete_table('account_userprofile_blocked')

        # Deleting model 'Relationship'
        db.delete_table('account_relationship')

        # Deleting model 'UserOptions'
        db.delete_table('account_useroptions')


    models = {
        'account.friendrequest': {
            'Meta': {'unique_together': "(('from_user', 'to_user'),)", 'object_name': 'FriendRequest'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'from_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'from_user'", 'to': "orm['account.UserProfile']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'to_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'to_user'", 'to': "orm['account.UserProfile']"})
        },
        'account.relationrequest': {
            'Meta': {'object_name': 'RelationRequest'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'from_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'relation_from'", 'to': "orm['account.UserProfile']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'to_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'relation_to'", 'to': "orm['account.UserProfile']"}),
            'type': ('django.db.models.fields.TextField', [], {'max_length': "'1'"})
        },
        'account.relationship': {
            'Meta': {'object_name': 'Relationship'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'from_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'from_people'", 'to': "orm['account.UserProfile']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': '1', 'max_length': "'1'"}),
            'to_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'to_people'", 'to': "orm['account.UserProfile']"})
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
            'bio_text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'birth_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'blocked': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'blocked_from'", 'symmetrical': 'False', 'to': "orm['account.UserProfile']"}),
            'cover_photo': ('django.db.models.fields.files.ImageField', [], {'default': "'uploads/images/bg_cover.png'", 'max_length': '100'}),
            'filters': ('django.db.models.fields.CharField', [], {'default': "'F'", 'max_length': "'10'"}),
            'followers': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'following'", 'symmetrical': 'False', 'through': "orm['account.Relationship']", 'to': "orm['account.UserProfile']"}),
            'friends': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'friends_rel_+'", 'to': "orm['account.UserProfile']"}),
            'hidden': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'hidden_from'", 'symmetrical': 'False', 'to': "orm['account.UserProfile']"}),
            'images_quote': ('django.db.models.fields.CharField', [], {'default': "'Whose woods these are I think I know, his house is in the village though.'", 'max_length': '70'}),
            'images_quote_author': ('django.db.models.fields.CharField', [], {'default': "'Robert Frost'", 'max_length': '20'}),
            'in_relationship': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['account.UserProfile']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'optional_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': "'200'"}),
            'photo': ('images.fields.ImageWithThumbField', [], {'default': "'uploads/images/noProfilePhoto.png'", 'max_length': '100'}),
            'relationtype': ('django.db.models.fields.CharField', [], {'max_length': "'1'", 'blank': 'True'}),
            'timezone': ('django.db.models.fields.CharField', [], {'max_length': "'200'", 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
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