from django.shortcuts import redirect
from functools import wraps


# ============================================
# Только admin
# ============================================
def admin_required(view_func):

    @wraps(view_func)

    def wrapper(request, *args, **kwargs):

        if (

            request.user.is_authenticated

            and request.user.role == 'admin'

        ):

            return view_func(
                request,
                *args,
                **kwargs
            )

        return redirect('/dashboard/')

    return wrapper


# ============================================
# Admin + Employee
# ============================================
def staff_required(view_func):

    @wraps(view_func)

    def wrapper(request, *args, **kwargs):

        if (

            request.user.is_authenticated

            and request.user.role in [
                'admin',
                'employee'
            ]

        ):

            return view_func(
                request,
                *args,
                **kwargs
            )

        return redirect('/dashboard/')

    return wrapper