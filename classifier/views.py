from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)
from django.contrib.auth import (
    login,
    logout
)
from django.contrib.auth.decorators import (
    login_required
)
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Ticket
from .forms import TicketForm
from .forms_auth import (
    RegisterForm,
    LoginForm
)
from .ml_model import predict_category
from .decorators import (
    admin_required,
    staff_required
)
from django.core.mail import send_mail
from django.utils.http import (
    urlsafe_base64_encode,
    urlsafe_base64_decode
)
from django.utils.encoding import (
    force_bytes,
    force_str
)
from django.contrib.auth import get_user_model
from .tokens import (
    email_verification_token
)

def get_user_tickets(user):

    # Admin и Employee видят все заявки
    if user.role in [
        'admin',
        'employee'
    ]:

        return Ticket.objects.all()

    # User видит только свои
    return Ticket.objects.filter(
        user=user
    )



def index(request):

    return render(
        request,
        'classifier/index.html'
    )



@login_required
def dashboard(request):

    tickets = get_user_tickets(
        request.user
    ).order_by('-created_at')

    total_tickets = tickets.count()

    new_tickets = tickets.filter(
        status='new'
    ).count()

    in_progress_tickets = tickets.filter(
        status='in_progress'
    ).count()

    done_tickets = tickets.filter(
        status='done'
    ).count()

    critical_tickets = tickets.filter(
        priority='critical'
    ).count()

    recent_tickets = tickets[:5]

    context = {

        'total_tickets': total_tickets,

        'new_tickets': new_tickets,

        'in_progress_tickets': in_progress_tickets,

        'done_tickets': done_tickets,

        'critical_tickets': critical_tickets,

        'recent_tickets': recent_tickets,

    }

    return render(

        request,

        'classifier/dashboard.html',

        context

    )



@login_required
def classify(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data['text']
            # AI анализ
            result = predict_category(text)
            category = result.get(
                'category',
                'Unknown'
            )
            confidence = result.get(
                'confidence',
                0
            )
            top_predictions = result.get(
                'top_predictions',
                []
            )
            # Создание обращения
            ticket = Ticket.objects.create(
                user=request.user,
                text=text,
                predicted_category=category,
                confidence=confidence,
                status='new',
                priority='medium'
            )
            messages.success(
                request,
                'Обращение успешно создано'
            )
            return render(
                request,
                'classifier/result.html',
                {
                    'ticket': ticket,
                    'confidence': confidence,
                    'top_predictions': top_predictions,
                }
            )
    else:
        form = TicketForm()
    return render(
        request,
        'classifier/classify.html',
        {
            'form': form
        }
    )


@login_required
def history(request):

    tickets = get_user_tickets(
        request.user
    )

    # Поиск
    search_query = request.GET.get('q')

    if search_query:

        tickets = tickets.filter(

            Q(text__icontains=search_query)

            |

            Q(predicted_category__icontains=search_query)

        )

    # Фильтр статуса
    status = request.GET.get('status')

    if status and status != 'all':

        tickets = tickets.filter(
            status=status
        )

    # Фильтр приоритета
    priority = request.GET.get('priority')

    if priority and priority != 'all':

        tickets = tickets.filter(
            priority=priority
        )

    tickets = tickets.order_by(
        '-created_at'
    )

    # Pagination
    paginator = Paginator(
        tickets,
        10
    )

    page_number = request.GET.get('page')

    tickets = paginator.get_page(
        page_number
    )

    context = {

        'tickets': tickets,

        'search_query': search_query,

        'selected_status': status,

        'selected_priority': priority,

    }

    return render(

        request,

        'classifier/history.html',

        context

    )


def register_view(request):
    if request.user.is_authenticated:
        return redirect('/dashboard/')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(
                commit=False
            )
            user.role = 'user'
            user.is_active = False
            user.save()
            uid = urlsafe_base64_encode(
                force_bytes(user.pk)
            )
            token = (
                email_verification_token.make_token(
                    user
                )
            )
            verification_link = (
                f'http://127.0.0.1:8000/verify-email/{uid}/{token}/'
            )
            send_mail(
                'Подтверждение регистрации',
                f'Перейдите по ссылке для подтверждения аккаунта:\n\n{verification_link}',
                None,
                [user.email],
                fail_silently=False,
            )
            messages.success(
                request,
                'Письмо подтверждения отправлено на email'
            )
            return redirect('/login/')
    else:
        form = RegisterForm()
    return render(
        request,
        'classifier/register.html',
        {
            'form': form
        }
    )


def login_view(request):

    if request.user.is_authenticated:

        return redirect('/dashboard/')

    if request.method == 'POST':

        form = LoginForm(

            request,

            data=request.POST

        )

        if form.is_valid():

            user = form.get_user()

            login(

                request,

                user

            )

            messages.success(

                request,

                'Вы успешно вошли в систему'

            )

            return redirect('/dashboard/')

    else:

        form = LoginForm()

    return render(

        request,

        'classifier/login.html',

        {

            'form': form

        }

    )



@login_required
def logout_view(request):

    logout(request)

    messages.info(

        request,

        'Вы вышли из аккаунта'

    )

    return redirect('/')



@login_required
@staff_required
def admin_panel(request):

    tickets = Ticket.objects.all().order_by(
        '-created_at'
    )

    context = {

        'tickets': tickets

    }

    return render(

        request,

        'classifier/admin_panel.html',

        context

    )


@login_required
def profile(request):

    tickets = Ticket.objects.filter(

        user=request.user

    ).order_by('-created_at')

    total_tickets = tickets.count()

    done_tickets = tickets.filter(
        status='done'
    ).count()

    context = {

        'tickets': tickets,

        'total_tickets': total_tickets,

        'done_tickets': done_tickets,

    }

    return render(

        request,

        'classifier/profile.html',

        context

    )


@login_required
@staff_required
def update_ticket_status(request, ticket_id):

    ticket = get_object_or_404(

        Ticket,

        id=ticket_id

    )

    if request.method == 'POST':

        ticket.status = request.POST.get(
            'status'
        )

        ticket.priority = request.POST.get(
            'priority'
        )

        ticket.admin_comment = request.POST.get(
            'admin_comment'
        )

        ticket.save()

        messages.success(

            request,

            'Статус обращения обновлён'

        )

        return redirect('/admin-panel/')

    return render(

        request,

        'classifier/update_ticket.html',

        {

            'ticket': ticket

        }

    )


@login_required
def ticket_detail(request, ticket_id):

    ticket = get_object_or_404(
        Ticket,
        id=ticket_id
    )

    if (
        request.user.role not in [
            'admin',
            'employee'
        ]
        and ticket.user != request.user
    ):
        return redirect('/dashboard/')
    return render(
        request,
        'classifier/ticket_detail.html',
        {
            'ticket': ticket
        }
    )


@login_required
@admin_required
def delete_ticket(request, ticket_id):

    ticket = get_object_or_404(
        Ticket,
        id=ticket_id
    )
    ticket.delete()
    messages.success(
        request,
        'Обращение удалено'
    )
    return redirect('/history/')

def verify_email(
    request,
    uidb64,
    token
):

    User = get_user_model()
    try:
        uid = force_str(
            urlsafe_base64_decode(uidb64)
        )
        user = User.objects.get(
            pk=uid
        )
    except Exception:
        user = None
    if (
        user is not None
        and
        email_verification_token.check_token(
            user,
            token
        )
    ):
        user.is_active = True
        user.save()
        messages.success(
            request,
            'Email успешно подтвержден'
        )
        return redirect('/login/')
    messages.error(
        request,
        'Ссылка недействительна'
    )
    return redirect('/login/')