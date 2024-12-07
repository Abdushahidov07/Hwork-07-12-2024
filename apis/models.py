from django.db import models
from django.utils import timezone

class MyManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted = False)
    
    def active(self):
        return self.get_queryset().filter(is_active=True)
    
    def deleted(self):
        return self.get_queryset().filter(is_deleted=True)
    
    def restore(self, obj):
        if obj.is_deleted:
            obj.restore()
            return obj
        return None

class BaseModel(models.Model):
    is_deleted = models.BooleanField(default=False)
    deleted_time=models.DateTimeField(null=True, blank=True)

    def delete(self):
        self.is_deleted = True
        self.deleted_time= timezone.now()
        self.save()
        
    def restore(self):
        self.is_deleted = False
        self.deleted_time = None
        self.save()
    class Meta:
        abstract = True
class Dish(BaseModel):
    CHOICE_TIME = (
        ("BREAKFEST","Завтрак"),
        ("LUNCH","Обед"),
        ("DINNER","Ужин"),
        ("dessert","Десерт"),
        ("Drinks","Напитки"),
        ("Snacks","Салаты")
    )
    name_dish = models.CharField(max_length=50)
    descriptions = models.TextField()
    time_category = models.CharField(max_length=50, choices=CHOICE_TIME)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    prf_time = models.CharField(max_length=50)
    img = models.ImageField(upload_to="media/images",)
    created_at = models.DateTimeField(auto_now=True, auto_now_add=False)
    is_active = models.BooleanField(default=True)
    objects = MyManager()
    def __str__(self):
        return self.name_dish

class Table(BaseModel):
    CHOICE_STATUS=(
        ("Full", "FULL"),
        ("Free", "Free"),

    )
    CHOICE_TABLE =(
        ("vip", "vip"),
        ("table", "Стол"),
        ("Cud", "Кад")
    )
    type = models.CharField(max_length=50, choices=CHOICE_TABLE)
    max_person = models.IntegerField()
    status = models.CharField(max_length=50, choices=CHOICE_STATUS, null=True)
    is_active = models.BooleanField(default=True)
    objects = MyManager()

    def __str__(self):
        return self.type
    

class Bill(BaseModel):
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    castumername = models.CharField(max_length=50)
    total_sum = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    is_paid = models.BooleanField(default=False,null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField( auto_now=True, auto_now_add=False)
    objects = MyManager()

    def save(self, *args, **kwargs):
        if self.is_paid:
            self.table.status = "Free"
            self.is_active = False
        else:
            self.table.status = "Full"
        self.table.save()
        super().save(*args, **kwargs) 
    def __str__(self):
        return self.castumername
    

class Order(BaseModel):
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='orders')
    count = models.IntegerField()
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    objects = MyManager()
    def save(self, *args, **kwargs):
        self.total = self.dish.price * self.count
        self.bill.total_sum += self.total 
        self.bill.save() 
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.dish} -> {self.bill}"
