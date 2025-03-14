from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.db.models import Q
from django.db.models import Count
from django.utils import timezone
from events.forms import EventModelForm,ParticipantForm,CategoryForm
from events.models import Event,Participant,Category
from django.contrib import messages
from datetime import datetime
from django.shortcuts import redirect

# def home_page(request):
#      return render(request, "dashboard/homepage.html")

def create_event(request):
    participants = Participant.objects.all()  
    form = EventModelForm()
    if request.method == "POST":
        form = EventModelForm(request.POST)  
        if form.is_valid():
            form.save()
            messages.success(request, "Event Created Successfully")
            return redirect('create-event')
    return render(request, 'event_form.html', {"form": form})

def create_participant(request):
    form = ParticipantForm()
    if request.method == "POST":
        form = ParticipantForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Participant Created Successfully")
            return redirect('create-participant') 
    return render(request, 'participant_form.html', {"form": form})

def create_category(request):
    form = CategoryForm()
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Category Created Successfully")
            return redirect('create-category') 
    return render(request, 'category_form.html', {"form": form})

def dashboard(request):
    today = timezone.localtime(timezone.now()).date()
    event_type = request.GET.get("type", "") 
    events = Event.objects.select_related('category').prefetch_related('participants').all()    
    event_counts = events.aggregate(
        total_events=Count('id'),
        upcoming_events=Count("id", filter=Q(date=today) | Q(date__gt=today)),
        past_events=Count('id', filter=Q(date__lt=today)),
    )
    participants=Participant.objects.all()
    event_participants = Event.objects.aggregate(
        total_participants=Count('participants', distinct=True)
    )
    total_participants = Participant.objects.count()
    if event_type == "total_participants":
        events = events.filter(date=today)  
    elif event_type == "total_events":
        events = events.all()
    elif event_type == "upcoming_events":
        events = events.filter(date__gte=today)
    elif event_type == "past_events":
        events = events.filter(date__lt=today)
    else:
        events = events.filter(date=today)
    
    context = {
        'events': events,
        'participants':participants,
        'total_participants':total_participants,
        'event_counts':event_counts,
        'event_participants':event_participants,
        
    }
    today_events = events.filter(date=today)
    print("Today's Events:", today_events) 
    return render(request, "dashboard/dashboard.html", context)

def base(request):
     return render(request,"dashboard/base.html")

def search(request):
    total_category = Category.objects.all()
    query = request.GET.get('q', '')
    category_query=request.GET.get('type','')
    events = Event.objects.all()
    first_date = request.GET.get('start_date', '')
    second_date = request.GET.get('end_date', '')
    if first_date and second_date:
        events = events.filter(date__gte=first_date, date__lte=second_date)
        print("Date:", first_date, " ", second_date)
    else:
        print("Skipping date")

    if category_query:
        events = events.filter(category__name=category_query)
    print("Category:",category_query)
    if query:
        events = events.filter(
            Q(name__icontains=query) | 
            Q(location__icontains=query)
        ).distinct()
    for event in events:
        event.participant_count = event.participants.count() 
    context = {
        'events': events,
        'query': query,
        'total_category': total_category,
    } 
    return render(request, 'dashboard/search_page.html', context)

def update_event(request, id):
    events = Event.objects.get(id=id)
    form = EventModelForm(instance=events)
    if request.method == "POST":
        form = EventModelForm(request.POST, instance=events)
        if form.is_valid():
            form.save()
            messages.success(request, "Event updated Successfully")
            return redirect('update',id)
    return render(request, 'event_form.html', {"form": form}) 

def delete_event(request,id):
    if request.method == "POST":
        events=Event.objects.get(id=id)
        events.delete()
        messages.success(request, "Event deleted Successfully")
        return redirect('dashboard')
    else:
        messages.success(request, "Something went wrong")
        return redirect('dashboard')

def event_page(request,id):
    event = Event.objects.get(id=id)
    event_participants = event.participants.all()
    context = {
        'event': event,
        'event_participants': event_participants
    }
    return render(request, 'dashboard/event_page.html', context)

def update_participant(request, id):
    participant = Participant.objects.get(id=id)
    form = ParticipantForm(instance=participant)
    if request.method == "POST":
        form = ParticipantForm(request.POST, instance=participant)
        if form.is_valid():
            form.save()
            messages.success(request, "Participant updated Successfully")
            return redirect('dashboard')
    return render(request, 'participant_form.html', {"form": form}) 

def delete_participant(request,id):
    if request.method == "POST":
        participant=Participant.objects.get(id=id)
        participant.delete()
        messages.success(request, "Participant deleted Successfully")
        return redirect('dashboard')
    else:
        messages.success(request, "Something went wrong")
        return redirect('dashboard')
