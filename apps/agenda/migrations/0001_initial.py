# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Events'
        db.create_table('agenda_events', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('page', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pages.Pages'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length='200')),
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
            ('date_end', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('privacy', self.gf('django.db.models.fields.CharField')(default='P', max_length=20)),
            ('allow_commenting', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('allow_sharing', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('agenda', ['Events'])

        # Adding M2M table for field tagged on 'Events'
        db.create_table('agenda_events_tagged', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('events', models.ForeignKey(orm['agenda.events'], null=False)),
            ('pages', models.ForeignKey(orm['pages.pages'], null=False))
        ))
        db.create_unique('agenda_events_tagged', ['events_id', 'pages_id'])

        # Adding model 'Locations'
        db.create_table('agenda_locations', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['agenda.Events'])),
            ('location', self.gf('django.db.models.fields.CharField')(max_length='2000', blank=True)),
            ('lat', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('lng', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
        ))
        db.send_create_signal('agenda', ['Locations'])


    def backwards(self, orm):
        # Deleting model 'Events'
        db.delete_table('agenda_events')

        # Removing M2M table for field tagged on 'Events'
        db.delete_table('agenda_events_tagged')

        # Deleting model 'Locations'
        db.delete_table('agenda_locations')


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
        'agenda.locations': {
            'Meta': {'object_name': 'Locations'},
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['agenda.Events']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lat': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'lng': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': "'2000'", 'blank': 'True'})
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
        }
    }

    complete_apps = ['agenda']