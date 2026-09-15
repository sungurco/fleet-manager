"""
Rol bazlı erişim kontrolü için yardımcı decorator ve mixin'ler.
Kullanım: @role_required(["ADMIN", "OPERASYON"]) veya class-based view'larda RoleRequiredMixin
"""
from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped(request, *args, **kwargs):
            if request.user.is_superuser or request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            raise PermissionDenied("Bu sayfaya erişim yetkiniz yok.")
        return _wrapped
    return decorator


class RoleRequiredMixin:
    allowed_roles = []

    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_superuser or request.user.role in self.allowed_roles):
            raise PermissionDenied("Bu sayfaya erişim yetkiniz yok.")
        return super().dispatch(request, *args, **kwargs)
