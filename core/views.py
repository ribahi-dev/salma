from datetime import datetime

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from bookings.forms import BookingForm
from bookings.models import Booking
from bookings.utils import calculate_available_slots
from rooms.forms import RoomForm
from rooms.models import Room
from users.forms import ProfileForm, RegisterForm
from users.models import CustomUser


def home_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        identifier = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        username = identifier

        if '@' in identifier:
            matched_user = CustomUser.objects.filter(email__iexact=identifier).first()
            if matched_user:
                username = matched_user.username

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        messages.error(request, "Identifiant ou mot de passe incorrect.")

    return render(request, 'registration/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Compte cree avec succes. Vous pouvez maintenant vous connecter.')
            return redirect('login')
        messages.error(request, 'Merci de corriger les erreurs du formulaire.')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def dashboard_view(request):
    today = timezone.localdate()
    scoped_bookings = Booking.objects.all() if request.user.is_staff else Booking.objects.filter(user=request.user)
    recent_bookings = scoped_bookings.select_related('room', 'user').order_by('-created_at')[:6]

    room_counts = Room.objects.filter(is_active=True).values('room_type').annotate(total=Count('id')).order_by('room_type')
    room_overview = {row['room_type']: row['total'] for row in room_counts}

    context = {
        'statistics': {
            'total_bookings': scoped_bookings.count(),
            'today_bookings': scoped_bookings.filter(date=today).count(),
            'upcoming_bookings': scoped_bookings.filter(date__gte=today, status__in=['EN_ATTENTE', 'CONFIRMEE']).count(),
            'confirmed_bookings': scoped_bookings.filter(status='CONFIRMEE').count(),
            'cancelled_bookings': scoped_bookings.filter(status='ANNULEE').count(),
            'active_rooms': Room.objects.filter(is_active=True).count(),
        },
        'recent_bookings': recent_bookings,
        'room_usage': Room.objects.filter(is_active=True).annotate(total=Count('booking')).order_by('-total', 'code')[:6],
        'room_overview': {
            'classrooms': room_overview.get(Room.TYPE_CLASSROOM, 0),
            'labs': room_overview.get(Room.TYPE_LAB, 0),
            'conferences': room_overview.get(Room.TYPE_CONFERENCE, 0),
        },
    }
    return render(request, 'sris/dashboard.html', context)


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil mis a jour avec succes.')
            return redirect('profile')
        messages.error(request, 'Merci de corriger les erreurs du formulaire.')
    else:
        form = ProfileForm(instance=request.user)

    return render(request, 'registration/profile.html', {'form': form, 'user_obj': request.user})


@login_required
def room_list_view(request):
    rooms = Room.objects.filter(is_active=True)
    capacity = request.GET.get('capacity')
    search = request.GET.get('search')
    equipment = request.GET.get('equipment')
    floor = request.GET.get('floor')
    room_type = request.GET.get('room_type')

    if capacity:
        try:
            rooms = rooms.filter(capacity__gte=int(capacity))
        except ValueError:
            messages.error(request, 'Capacite invalide.')

    if search:
        rooms = rooms.filter(
            Q(code__icontains=search)
            | Q(name__icontains=search)
            | Q(location__icontains=search)
            | Q(description__icontains=search)
        )

    if equipment:
        rooms = rooms.filter(equipment__icontains=equipment)

    if floor:
        try:
            rooms = rooms.filter(floor=int(floor))
        except ValueError:
            messages.error(request, 'Etage invalide.')

    if room_type:
        rooms = rooms.filter(room_type=room_type)

    paginator = Paginator(rooms.order_by('floor', 'code'), 12)
    page_number = request.GET.get('page')
    rooms = paginator.get_page(page_number)

    return render(
        request,
        'rooms/room_list.html',
        {
            'rooms': rooms,
            'room_type_choices': Room.ROOM_TYPE_CHOICES,
            'floors': range(1, 7),
        },
    )


@login_required
def room_detail_view(request, pk):
    room = get_object_or_404(Room, pk=pk)
    bookings = Booking.objects.filter(room=room, date__gte=timezone.localdate()).select_related('user').order_by('date', 'start_time')[:12]
    return render(request, 'rooms/room_detail.html', {'room': room, 'bookings': bookings})


@login_required
def room_create_view(request):
    if not request.user.is_staff:
        messages.error(request, "Vous n'avez pas la permission d'acceder a cette page.")
        return redirect('room_list')

    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Salle creee avec succes.')
            return redirect('room_list')
        messages.error(request, 'Merci de corriger les erreurs du formulaire.')
    else:
        form = RoomForm()

    return render(request, 'rooms/room_form.html', {'form': form})


@login_required
def room_update_view(request, pk):
    if not request.user.is_staff:
        messages.error(request, "Vous n'avez pas la permission d'acceder a cette page.")
        return redirect('room_list')

    room = get_object_or_404(Room, pk=pk)
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            messages.success(request, 'Salle mise a jour avec succes.')
            return redirect('room_detail', pk=room.pk)
        messages.error(request, 'Merci de corriger les erreurs du formulaire.')
    else:
        form = RoomForm(instance=room)

    return render(request, 'rooms/room_form.html', {'form': form, 'room': room})


@login_required
def room_delete_view(request, pk):
    if not request.user.is_staff:
        messages.error(request, "Vous n'avez pas la permission d'acceder a cette page.")
        return redirect('room_list')

    room = get_object_or_404(Room, pk=pk)
    if request.method != 'POST':
        messages.error(request, 'La suppression doit etre confirmee.')
        return redirect('room_detail', pk=room.pk)

    room.delete()
    messages.success(request, 'Salle supprimee avec succes.')
    return redirect('room_list')


@login_required
def booking_list_view(request):
    bookings = Booking.objects.all() if request.user.is_staff else Booking.objects.filter(user=request.user)
    status = request.GET.get('status')
    booking_date = request.GET.get('date')
    room_id = request.GET.get('room')

    if status:
        bookings = bookings.filter(status=status)
    if booking_date:
        bookings = bookings.filter(date=booking_date)
    if room_id:
        bookings = bookings.filter(room_id=room_id)

    bookings = bookings.select_related('room', 'user').order_by('-created_at')
    paginator = Paginator(bookings, 12)
    page_number = request.GET.get('page')
    bookings = paginator.get_page(page_number)

    rooms = Room.objects.filter(is_active=True).order_by('floor', 'code')
    return render(request, 'bookings/booking_list.html', {'bookings': bookings, 'rooms': rooms})


@login_required
def booking_create_view(request):
    rooms = Room.objects.filter(is_active=True).order_by('floor', 'code')
    today = timezone.localdate().strftime('%Y-%m-%d')

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            try:
                booking.save()
                messages.success(request, 'Reservation creee avec succes.')
                return redirect('booking_list')
            except Exception as exc:
                messages.error(request, str(exc))
        else:
            messages.error(request, 'Merci de corriger les erreurs du formulaire.')
    else:
        initial_data = {}
        if request.GET.get('date'):
            initial_data['date'] = request.GET.get('date')
        if request.GET.get('start'):
            initial_data['start_time'] = request.GET.get('start')
        if request.GET.get('end'):
            initial_data['end_time'] = request.GET.get('end')
        if request.GET.get('room'):
            initial_data['room'] = request.GET.get('room')
        form = BookingForm(initial=initial_data)

    return render(request, 'bookings/booking_form.html', {'form': form, 'rooms': rooms, 'today': today})


@login_required
def booking_detail_view(request, pk):
    booking = get_object_or_404(Booking.objects.select_related('room', 'user'), pk=pk)
    if booking.user != request.user and not request.user.is_staff:
        messages.error(request, "Vous n'avez pas la permission de voir cette reservation.")
        return redirect('booking_list')
    return render(request, 'bookings/booking_detail.html', {'booking': booking})


@login_required
def booking_update_view(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if booking.user != request.user and not request.user.is_staff:
        messages.error(request, "Vous n'avez pas la permission de modifier cette reservation.")
        return redirect('booking_list')

    if booking.status == 'ANNULEE':
        messages.error(request, 'Impossible de modifier une reservation annulee.')
        return redirect('booking_list')

    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Reservation mise a jour avec succes.')
                return redirect('booking_list')
            except Exception as exc:
                messages.error(request, str(exc))
        else:
            messages.error(request, 'Merci de corriger les erreurs du formulaire.')
    else:
        form = BookingForm(instance=booking)

    rooms = Room.objects.filter(is_active=True).order_by('floor', 'code')
    return render(request, 'bookings/booking_form.html', {'form': form, 'rooms': rooms, 'booking': booking})


@login_required
def booking_cancel_view(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if booking.user != request.user and not request.user.is_staff:
        messages.error(request, "Vous n'avez pas la permission d'annuler cette reservation.")
        return redirect('booking_list')

    if booking.status == 'ANNULEE':
        messages.error(request, 'Cette reservation est deja annulee.')
        return redirect('booking_list')

    if request.method != 'POST':
        messages.error(request, "L'annulation doit etre confirmee.")
        return redirect('booking_list')

    booking.status = 'ANNULEE'
    booking.save()
    messages.success(request, 'Reservation annulee avec succes.')
    return redirect('booking_list')


@login_required
def booking_confirm_view(request, pk):
    if not request.user.is_staff:
        messages.error(request, "Vous n'avez pas la permission de confirmer cette reservation.")
        return redirect('booking_list')

    booking = get_object_or_404(Booking, pk=pk)
    if request.method != 'POST':
        messages.error(request, 'La confirmation doit etre envoyee via le formulaire.')
        return redirect('booking_list')

    if booking.status == 'CONFIRMEE':
        messages.info(request, 'Cette reservation est deja confirmee.')
        return redirect('booking_list')

    if booking.status == 'ANNULEE':
        messages.error(request, 'Impossible de confirmer une reservation annulee.')
        return redirect('booking_list')

    booking.status = 'CONFIRMEE'
    booking.save()
    messages.success(request, 'Reservation confirmee avec succes.')
    return redirect('booking_list')


@login_required
def booking_calendar_view(request):
    rooms = Room.objects.filter(is_active=True).order_by('floor', 'code')
    return render(request, 'bookings/calendar.html', {'rooms': rooms})


@login_required
def booking_availability_api(request):
    room_id = request.GET.get('room')
    booking_date = request.GET.get('date')

    if not room_id or not booking_date:
        return JsonResponse({'error': 'Parametres manquants'}, status=400)

    try:
        room = Room.objects.get(id=room_id)
    except Room.DoesNotExist:
        return JsonResponse({'error': 'Salle non trouvee'}, status=404)

    bookings = Booking.objects.filter(
        room=room,
        date=booking_date,
        status__in=['EN_ATTENTE', 'CONFIRMEE'],
    ).order_by('start_time').values('start_time', 'end_time', 'user__username', 'status')

    busy_times = [(booking['start_time'], booking['end_time']) for booking in bookings]
    return JsonResponse(
        {
            'room': {
                'id': room.id,
                'code': room.code,
                'name': room.display_name,
                'capacity': room.capacity,
                'room_type': room.get_room_type_display(),
            },
            'date': booking_date,
            'bookings': list(bookings),
            'availability': calculate_available_slots(busy_times),
        }
    )


@login_required
def booking_calendar_api(request):
    room_id = request.GET.get('room')
    status = request.GET.get('status')

    bookings = Booking.objects.filter(status__in=['EN_ATTENTE', 'CONFIRMEE']).select_related('room', 'user')

    if room_id:
        bookings = bookings.filter(room_id=room_id)
    if status:
        bookings = bookings.filter(status=status)

    events = []
    for booking in bookings.order_by('date', 'start_time'):
        start_value = datetime.combine(booking.date, booking.start_time).isoformat()
        end_value = datetime.combine(booking.date, booking.end_time).isoformat()
        title = f'{booking.room.code} - {booking.purpose}'
        events.append(
            {
                'id': booking.id,
                'title': title,
                'start': start_value,
                'end': end_value,
                'status': booking.status,
                'room_name': booking.room.display_name,
                'room_code': booking.room.code,
                'user_name': booking.user.full_name_or_username,
                'purpose': booking.purpose,
            }
        )

    return JsonResponse(events, safe=False)
