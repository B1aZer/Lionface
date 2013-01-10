# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'PageRequest'
        db.create_table('pages_pagerequest', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('from_page', self.gf('django.db.models.fields.related.ForeignKey')(related_name='from_page', to=orm['pages.Pages'])),
            ('to_page', self.gf('django.db.models.fields.related.ForeignKey')(related_name='to_page', to=orm['pages.Pages'])),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='from_event', null=True, to=orm['agenda.Events'])),
            ('type', self.gf('django.db.models.fields.CharField')(default='PR', max_length='2')),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('is_hidden', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_accepted', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('pages', ['PageRequest'])

        # Adding model 'PagePositions'
        db.create_table('pages_pagepositions', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('to_page', self.gf('django.db.models.fields.related.ForeignKey')(related_name='posto_page', to=orm['pages.Pages'])),
            ('from_page', self.gf('django.db.models.fields.related.ForeignKey')(related_name='postfrom_page', to=orm['pages.Pages'])),
            ('position', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('pages', ['PagePositions'])

        # Adding model 'PageLoves'
        db.create_table('pages_pageloves', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('page', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pages.Pages'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['account.UserProfile'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default='A', max_length='1')),
        ))
        db.send_create_signal('pages', ['PageLoves'])

        # Adding model 'PageFavourites'
        db.create_table('pages_pagefavourites', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('page', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pages.Pages'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['account.UserProfile'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('position', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('pages', ['PageFavourites'])

        # Adding model 'Pages'
        db.create_table('pages_pages', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length='200')),
            ('loves', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('loves_limit', self.gf('django.db.models.fields.IntegerField')(default=100)),
            ('username', self.gf('django.db.models.fields.CharField')(unique=True, max_length='200')),
            ('url', self.gf('django.db.models.fields.URLField')(max_length='2000', null=True, blank=True)),
            ('content', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='pages', to=orm['account.UserProfile'])),
            ('type', self.gf('django.db.models.fields.CharField')(max_length='2')),
            ('category', self.gf('django.db.models.fields.CharField')(default='Undefined', max_length=100)),
            ('cover_photo', self.gf('django.db.models.fields.files.ImageField')(default='uploads/images/noCoverImage.png', max_length=100)),
            ('photo', self.gf('images.fields.ImageWithThumbField')(default='uploads/images/noProfilePhoto.png', max_length=100)),
            ('has_employees', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('text_employees', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('has_interns', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('text_interns', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('has_volunteers', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('text_volunteers', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('post_update', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('for_deletion', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('featured', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_disabled', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('exempt', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('pages', ['Pages'])

        # Adding M2M table for field friends on 'Pages'
        db.create_table('pages_pages_friends', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_pages', models.ForeignKey(orm['pages.pages'], null=False)),
            ('to_pages', models.ForeignKey(orm['pages.pages'], null=False))
        ))
        db.create_unique('pages_pages_friends', ['from_pages_id', 'to_pages_id'])

        # Adding M2M table for field admins on 'Pages'
        db.create_table('pages_pages_admins', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('pages', models.ForeignKey(orm['pages.pages'], null=False)),
            ('userprofile', models.ForeignKey(orm['account.userprofile'], null=False))
        ))
        db.create_unique('pages_pages_admins', ['pages_id', 'userprofile_id'])

        # Adding model 'Membership'
        db.create_table('pages_membership', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['account.UserProfile'])),
            ('page', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pages.Pages'])),
            ('type', self.gf('django.db.models.fields.CharField')(max_length='2')),
            ('from_date', self.gf('django.db.models.fields.DateField')()),
            ('to_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('is_confirmed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_present', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_new', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('pages', ['Membership'])

        # Adding model 'Topics'
        db.create_table('pages_topics', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length='2000')),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['account.UserProfile'])),
            ('page', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pages.Pages'])),
            ('privacy', self.gf('django.db.models.fields.CharField')(default='P', max_length=1)),
            ('members', self.gf('django.db.models.fields.CharField')(default='A', max_length=20)),
            ('content', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('pages', ['Topics'])

        # Adding M2M table for field tagged on 'Topics'
        db.create_table('pages_topics_tagged', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('topics', models.ForeignKey(orm['pages.topics'], null=False)),
            ('pages', models.ForeignKey(orm['pages.pages'], null=False))
        ))
        db.create_unique('pages_topics_tagged', ['topics_id', 'pages_id'])

        # Adding M2M table for field viewed on 'Topics'
        db.create_table('pages_topics_viewed', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('topics', models.ForeignKey(orm['pages.topics'], null=False)),
            ('userprofile', models.ForeignKey(orm['account.userprofile'], null=False))
        ))
        db.create_unique('pages_topics_viewed', ['topics_id', 'userprofile_id'])


    def backwards(self, orm):
        # Deleting model 'PageRequest'
        db.delete_table('pages_pagerequest')

        # Deleting model 'PagePositions'
        db.delete_table('pages_pagepositions')

        # Deleting model 'PageLoves'
        db.delete_table('pages_pageloves')

        # Deleting model 'PageFavourites'
        db.delete_table('pages_pagefavourites')

        # Deleting model 'Pages'
        db.delete_table('pages_pages')

        # Removing M2M table for field friends on 'Pages'
        db.delete_table('pages_pages_friends')

        # Removing M2M table for field admins on 'Pages'
        db.delete_table('pages_pages_admins')

        # Deleting model 'Membership'
        db.delete_table('pages_membership')

        # Deleting model 'Topics'
        db.delete_table('pages_topics')

        # Removing M2M table for field tagged on 'Topics'
        db.delete_table('pages_topics_tagged')

        # Removing M2M table for field viewed on 'Topics'
        db.delete_table('pages_topics_viewed')


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
        'agenda.events': {
            'Meta': {'object_name': 'Events'},
            'allow_commenting': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'allow_sharing': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'date_end': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': "'200'"}),
            'page': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pages.Pages']"}),
            'privacy': ('django.db.models.fields.CharField', [], {'default': "'P'", 'max_length': '20'}),
            'tagged': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'tagged_in'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['pages.Pages']"})
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
        'pages.pagefavourites': {
            'Meta': {'object_name': 'PageFavourites'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'page': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pages.Pages']"}),
            'position': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['account.UserProfile']"})
        },
        'pages.pageloves': {
            'Meta': {'object_name': 'PageLoves'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'page': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pages.Pages']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'A'", 'max_length': "'1'"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['account.UserProfile']"})
        },
        'pages.pagepositions': {
            'Meta': {'object_name': 'PagePositions'},
            'from_page': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'postfrom_page'", 'to': "orm['pages.Pages']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'position': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'to_page': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'posto_page'", 'to': "orm['pages.Pages']"})
        },
        'pages.pagerequest': {
            'Meta': {'object_name': 'PageRequest'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'from_event'", 'null': 'True', 'to': "orm['agenda.Events']"}),
            'from_page': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'from_page'", 'to': "orm['pages.Pages']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_accepted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'to_page': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'to_page'", 'to': "orm['pages.Pages']"}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'PR'", 'max_length': "'2'"})
        },
        'pages.pages': {
            'Meta': {'object_name': 'Pages'},
            'admins': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'pages_admin'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['account.UserProfile']"}),
            'category': ('django.db.models.fields.CharField', [], {'default': "'Undefined'", 'max_length': '100'}),
            'content': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'cover_photo': ('django.db.models.fields.files.ImageField', [], {'default': "'uploads/images/noCoverImage.png'", 'max_length': '100'}),
            'exempt': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'featured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'for_deletion': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'friends': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'friends_rel_+'", 'to': "orm['pages.Pages']"}),
            'has_employees': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'has_interns': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'has_volunteers': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_disabled': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'loves': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'loves_limit': ('django.db.models.fields.IntegerField', [], {'default': '100'}),
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
            'users_favourites': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'pages_favourites'", 'to': "orm['account.UserProfile']", 'through': "orm['pages.PageFavourites']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'users_loved': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'pages_loved'", 'to': "orm['account.UserProfile']", 'through': "orm['pages.PageLoves']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'})
        },
        'pages.topics': {
            'Meta': {'object_name': 'Topics'},
            'content': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'members': ('django.db.models.fields.CharField', [], {'default': "'A'", 'max_length': '20'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': "'2000'"}),
            'page': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pages.Pages']"}),
            'privacy': ('django.db.models.fields.CharField', [], {'default': "'P'", 'max_length': '1'}),
            'tagged': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'tagged_in_topics'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['pages.Pages']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['account.UserProfile']"}),
            'viewed': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'viewed_topics'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['account.UserProfile']"})
        }
    }

    complete_apps = ['pages']