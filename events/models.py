from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description=models.TextField()
    def __str__(self):
        return self.name
class Participant(models.Model):
    name=models.CharField(max_length=255)
    email=models.EmailField(unique=True)
    def __str__(self):
        return self.name
    
class Event(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='events_category' )
    participants = models.ManyToManyField(Participant, related_name='event_participant', blank=True)

    def __str__(self):
        return f"{self.name} - {self.date}" 
    

