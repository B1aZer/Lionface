from django.db import models
from account.models import UserProfile
from django.core.validators import validate_slug

PAGE_TYPE = (
        ('BS','Business Page'),
        ('NP','Nonprofit Page'),
)

PAGE_CATEGORY = (
    ('undefined',               'Undefined'),
    ('accomodation',               'Accomodation'),
    ('airline',                    'Airline'),
    ('automotive',                 'Automotive'),
    ('automotive_dealer',          'Automotive (Dealer)'),
    ('automotive_service',         'Automotive (Service)'),
    ('bank',                       'Bank'),
    ('bar_pub',                    'Bar/Pub '),
    ('bar_club',                   'Bar/Club'),
    ('computer_software',          'Computer (Software)'),
    ('computer_gadget_hardware',   'Computer/Gadget (Hardware)'),
    ('consultant',                 'Consultant'),
    ('convenience_store',          'Convenience Store'),
    ('energy',                     'Energy'),
    ('entertainment_cinema',       'Entertainment (Cinema)'),
    ('entertainment_performance',  'Entertainment (Performance)'),
    ('fashion_brand',              'Fashion (Brand)'),
    ('fashion_cosmetic_brand',     'Fashion (Cosmetic Brand)'),
    ('fashion_footwear_brand',     'Fashion (Footwear Brand)'),
    ('food_drink_brand/supplier',  'Food/Drink (Brand/Supplier)'),
    ('food_drink_cafe',            'Food/Drink (Cafe)'),
    ('food_drink_counter_served',  'Food/Drink (Counter Served)'),
    ('food_drink_drive_thru',      'Food/Drink (Drive Thru)'),
    ('food_drink_waitstaff_served','Food/Drink (Waitstaff Served)'),
    ('groceries',                  'Groceries'),
    ('industrial',                 'Industrial'),
    ('insurance',                  'Insurance'),
    ('health_treatment',           'Health (Treatment)'),
    ('health_gym_studio',          'Health (Gym/Studio)'),
    ('media',                      'Media'),
    ('media_internet',             'Media (Internet)'),
    ('media_print',                'Media (Print)'),
    ('media_social',               'Media (Social)'),
    ('media_tv_movie',             'Media (TV/Movie)'),
    ('phone_internet_provider',    'Phone/Internet Provider'),
    ('recreation',                 'Recreation'),
    ('recreation_theme_water_park','Recreation (Theme/Water Park)'),
    ('resort_spa',                 'Resort/Spa'),
    ('retail',                     'Retail'),
    ('retail_art',                 'Retail (Art)'),
    ('retail_clothing',            'Retail (Clothing)'),
    ('retail_electronics',         'Retail (Electronics)'),
    ('retail_footwear',            'Retail (Footwear)'),
    ('retail_home_improvement',    'Retail (Home Improvement)'),
    ('retail_office',              'Retail (Office)'),
    ('retail_pet',                 'Retail (Pet)'),
    ('retail_specialty',           'Retail (Specialty)'),
    ('retail_sports_recreation',   'Retail (Sports/Recreation)'),
    ('services',                   'Services'),
    ('services_accounting',        'Services (Accounting)'),
    ('services_legal',             'Services (Legal)'),
    ('services_web',               'Services (Web)'),
    ('travel',                     'Travel'),
)

class Pages(models.Model):
    name = models.CharField(max_length='200')
    loves = models.IntegerField(default=0)
    username = models.CharField(max_length='200',validators=[validate_slug], unique=True)
    user = models.ForeignKey(UserProfile, related_name='pages')
    users_loved = models.ManyToManyField(UserProfile, related_name='pages_loved', null=True, blank=True)
    type = models.CharField(max_length='2', choices=PAGE_TYPE)
    category = models.CharField(max_length=100,
                                      choices=PAGE_CATEGORY,
                                      default='undefined')

    class Meta:
        verbose_name = "Page"
        verbose_name_plural = "Pages"

    def get_lovers(self):
        return self.users_loved.all()
