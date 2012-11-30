# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'PageSharePost'
        db.create_table('post_pagesharepost', (
            ('pagepost_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['post.PagePost'], unique=True, primary_key=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'], null=True, blank=True)),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('post', ['PageSharePost'])


    def backwards(self, orm):
        # Deleting model 'PageSharePost'
        db.delete_table('post_pagesharepost')


    models = {
        'account.relationship': {
            'Meta': {'object_name': 'Relationship'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'from_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'from_people'", 'to': "orm['account.UserProfile']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': '1', 'max_length': "'1'"}),
            'to_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'to_people'", 'to': "orm['account.UserProfile']"})
        },
        'account.userprofile': {
            'Meta': {'object_name': 'UserProfile', '_ormbases': ['auth.User']},
            'blocked': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'blocked_from'", 'symmetrical': 'False', 'to': "orm['account.UserProfile']"}),
            'filters': ('django.db.models.fields.CharField', [], {'default': "'F'", 'max_length': "'10'"}),
            'followers': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'following'", 'symmetrical': 'False', 'through': "orm['account.Relationship']", 'to': "orm['account.UserProfile']"}),
            'friends': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'friends_rel_+'", 'to': "orm['account.UserProfile']"}),
            'hidden': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'hidden_from'", 'symmetrical': 'False', 'to': "orm['account.UserProfile']"}),
            'optional_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': "'200'"}),
            'photo': ('images.fields.ImageWithThumbField', [], {'default': "'uploads/images/noProfilePhoto.png'", 'max_length': '100'}),
            'timezone': ('django.db.models.fields.CharField', [], {'max_length': "'200'", 'blank': 'True'}),
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
        },
        'pages.membership': {
            'Meta': {'object_name': 'Membership'},
            'from_date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_confirmed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_new': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_present': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'page': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pages.Pages']"}),
            'to_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': "'2'"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['account.UserProfile']"})
        },
        'pages.pages': {
            'Meta': {'object_name': 'Pages'},
            'admins': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'pages_admin'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['account.UserProfile']"}),
            'category': ('django.db.models.fields.CharField', [], {'default': "'undefined'", 'max_length': '100'}),
            'content': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'cover_photo': ('django.db.models.fields.files.ImageField', [], {'default': "'uploads/images/noCoverImage.png'", 'max_length': '100'}),
            'friends': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'friends_rel_+'", 'to': "orm['pages.Pages']"}),
            'has_employees': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'has_interns': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'has_volunteers': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'loves': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'members': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'member_of'", 'symmetrical': 'False', 'through': "orm['pages.Membership']", 'to': "orm['account.UserProfile']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': "'200'"}),
            'photo': ('images.fields.ImageWithThumbField', [], {'default': "'uploads/images/noProfilePhoto.png'", 'max_length': '100'}),
            'post_update': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'text_employees': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'text_interns': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'text_volunteers': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': "'2'"}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': "'2000'", 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'pages'", 'to': "orm['account.UserProfile']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': "'200'"}),
            'users_loved': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'pages_loved'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['account.UserProfile']"})
        },
        'post.albums': {
            'Meta': {'object_name': 'Albums'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'position': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['account.UserProfile']"})
        },
        'post.contentpost': {
            'Meta': {'object_name': 'ContentPost', '_ormbases': ['post.Post']},
            'content': ('django.db.models.fields.CharField', [], {'max_length': '5000'}),
            'post_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['post.Post']", 'unique': 'True', 'primary_key': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        },
        'post.feedbackpost': {
            'Meta': {'object_name': 'FeedbackPost', '_ormbases': ['post.Post']},
            'agreed': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'feedback_votes_agreed'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['account.UserProfile']"}),
            'content': ('django.db.models.fields.CharField', [], {'max_length': '5000'}),
            'disagreed': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'feedback_votes_disagreed'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['account.UserProfile']"}),
            'page': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'feedback_posts'", 'to': "orm['pages.Pages']"}),
            'post_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['post.Post']", 'unique': 'True', 'primary_key': 'True'}),
            'rating': ('django.db.models.fields.IntegerField', [], {})
        },
        'post.friendpost': {
            'Meta': {'object_name': 'FriendPost', '_ormbases': ['post.Post']},
            'friend': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['account.UserProfile']"}),
            'post_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['post.Post']", 'unique': 'True', 'primary_key': 'True'})
        },
        'post.newsitem': {
            'Meta': {'unique_together': "(('user', 'post'),)", 'object_name': 'NewsItem'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'post': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['post.Post']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['account.UserProfile']"})
        },
        'post.pagepost': {
            'Meta': {'object_name': 'PagePost', '_ormbases': ['post.Post']},
            'content': ('django.db.models.fields.CharField', [], {'max_length': '5000'}),
            'page': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'posts'", 'to': "orm['pages.Pages']"}),
            'post_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['post.Post']", 'unique': 'True', 'primary_key': 'True'})
        },
        'post.pagesharepost': {
            'Meta': {'object_name': 'PageSharePost', '_ormbases': ['post.PagePost']},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'pagepost_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['post.PagePost']", 'unique': 'True', 'primary_key': 'True'})
        },
        'post.post': {
            'Meta': {'object_name': 'Post'},
            'album': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'posts'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': "orm['post.Albums']"}),
            'allow_commenting': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'allow_sharing': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'following': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'follows'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['account.UserProfile']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'loves': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'shared': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['tags.Tag']", 'symmetrical': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user'", 'to': "orm['account.UserProfile']"}),
            'user_to': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'user_to'", 'null': 'True', 'to': "orm['account.UserProfile']"}),
            'users_loved': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'posts_loved'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['account.UserProfile']"})
        },
        'post.sharepost': {
            'Meta': {'object_name': 'SharePost', '_ormbases': ['post.Post']},
            'content': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            'id_news': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'post_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['post.Post']", 'unique': 'True', 'primary_key': 'True'})
        },
        'tags.tag': {
            'Meta': {'object_name': 'Tag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['post']