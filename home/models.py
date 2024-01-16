from django.db import models

class Watch(models.Model):
    GENDER_CHOICES = [
        ('Men', 'Men'),
        ('Unisex', 'Unisex'),
        ('Women', 'Women'),
    ]

    BRAND_CHOICES = [
        ('Amazfit', 'Amazfit'),
        ('Anne Klein', 'Anne Klein'),
        ('Armani Exchange', 'Armani Exchange'),
        ('Calvin Klein', 'Calvin Klein'),
        ('Casio', 'Casio'),
        ('Coach', 'Coach'),
        ('Daniel Wellington', 'Daniel Wellington'),
        ('Diesel', 'Diesel'),
        ('Emporio Armani', 'Emporio Armani'),
        ('Fitbit', 'Fitbit'),
        ('Fossil', 'Fossil'),
        ('Fossil Smartwatch', 'Fossil Smartwatch'),
        ('G-Shock', 'G-Shock'),
        ('GC', 'GC'),
        ('Guess', 'Guess'),
        ('Hugo Boss', 'Hugo Boss'),
        ('Kenneth Cole', 'Kenneth Cole'),
        ('Michael Kors', 'Michael Kors'),
        ('Movado', 'Movado'),
        ('Obaku', 'Obaku'),
        ('Olivia Burton', 'Olivia Burton'),
        ('Police', 'Police'),
        ('Skagen', 'Skagen'),
        ('Titan', 'Titan'),
        ('Titan Smart', 'Titan Smart'),
        ('Tommy Hilfiger', 'Tommy Hilfiger'),
        ('Versace', 'Versace'),
        ('Xylys', 'Xylys'),
    ]

    STYLE_CHOICES = [
        ('Adventure', 'Adventure'),
        ('Bling', 'Bling'),
        ('Casual', 'Casual'),
        ('Dressy', 'Dressy'),
        ('Fashion', 'Fashion'),
        ('Fitness', 'Fitness'),
        ('Formal', 'Formal'),
        ('Minimalistic', 'Minimalistic'),
        ('Party', 'Party'),
        ('Sporty', 'Sporty'),
    ]

    STRAP_MATERIAL_CHOICES = [
        ('Acetate', 'Acetate'),
        ('Alloy', 'Alloy'),
        ('Ceramic', 'Ceramic'),
        ('Fabric', 'Fabric'),
        ('Gold', 'Gold'),
        ('Leather', 'Leather'),
        ('Metal', 'Metal'),
        ('Nylon', 'Nylon'),
        ('PU', 'PU'),
        ('Plastic', 'Plastic'),
        ('Polyurethane', 'Polyurethane'),
        ('Polyvinyl Chloride', 'Polyvinyl Chloride'),
        ('Pvc', 'Pvc'),
        ('Resin', 'Resin'),
        ('Rubber', 'Rubber'),
        ('Silicon', 'Silicon'),
        ('Silicone', 'Silicone'),
        ('Stainless Steel', 'Stainless Steel'),
        ('Stainless Steel & Ceramic', 'Stainless Steel & Ceramic'),
        ('Stainless Steel Mesh Band', 'Stainless Steel Mesh Band'),
        ('Textile', 'Textile'),
        ('mesh', 'Mesh'),
    ]

    DIAL_TYPE_CHOICES = [
        ('Analog', 'Analog'),
        ('Analog & Digital', 'Analog & Digital'),
        ('Digital', 'Digital'),
        ('Roman', 'Roman'),
        ('Smart', 'Smart'),
    ]

    DIAL_COLOUR_CHOICES = [
        ('Black', 'Black'),
        ('Blue', 'Blue'),
        ('Gold', 'Gold'),
        ('Pink', 'Pink'),
        ('White', 'White'),
    ]

    DIAL_SHAPE_CHOICES = [
        ('Octagonal', 'Octagonal'),
        ('Oval', 'Oval'),
        ('Polygon', 'Polygon'),
        ('Rectangle', 'Rectangle'),
        ('Rectangular', 'Rectangular'),
        ('Round', 'Round'),
        ('Square', 'Square'),
        ('Tonneau', 'Tonneau'),
        ('Triangle', 'Triangle'),
    ]

    watch_name = models.CharField(max_length=100,blank=True,null=True)
    watch_thumbnail = models.ImageField(upload_to='watch_thumbnails/',blank=True,null=True)
    brands = models.CharField(max_length=30, choices=BRAND_CHOICES,blank=True,null=True)
    watch_details = models.TextField(blank=True,null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,blank=True,null=True)
    discount = models.IntegerField(default=0,blank=True,null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES,blank=True,null=True)
    dial_type = models.CharField(max_length=20, choices=DIAL_TYPE_CHOICES,blank=True,null=True)
    dial_colour = models.CharField(max_length=20, choices=DIAL_COLOUR_CHOICES,blank=True,null=True)
    dial_shape = models.CharField(max_length=20, choices=DIAL_SHAPE_CHOICES,blank=True,null=True)
    style = models.CharField(max_length=20, choices=STYLE_CHOICES,blank=True,null=True)
    strap_material = models.CharField(max_length=30, choices=STRAP_MATERIAL_CHOICES,blank=True,null=True)

    def actual_price(self):
        return self.price - (self.price * self.discount / 100)

    def __str__(self):
        return self.watch_name
