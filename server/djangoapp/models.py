from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class CarMake(models.Model):
    name = models.CharField(max_length=80, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class CarModel(models.Model):
    car_make = models.ForeignKey(CarMake, on_delete=models.CASCADE, related_name='models')
    name = models.CharField(max_length=80)
    type = models.CharField(max_length=20, choices=[
        ('Sedan', 'Sedan'), ('SUV', 'SUV'), ('WAGON', 'Wagon'), ('Hatchback', 'Hatchback'),
        ('Truck', 'Truck'), ('Coupe', 'Coupe'), ('Convertible', 'Convertible'), ('Minivan', 'Minivan'),
    ])
    year = models.PositiveIntegerField(validators=[MinValueValidator(2015), MaxValueValidator(2026)])

    class Meta:
        constraints = [models.UniqueConstraint(fields=['car_make', 'name', 'year'], name='unique_car_model_year')]

    def __str__(self):
        return f'{self.car_make.name} {self.name} ({self.year})'
