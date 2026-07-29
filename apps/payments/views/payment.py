import logging

from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.payments.serializers import CreatePaymentSerializer, PaymentSerializer, PaymentListSerializer
from apps.payments.services.payment_service import PaymentService
from apps.shared.middlewares.permission import IsAdminOrOwner
from apps.shared.utils.response import CustomResponse

logger = logging.getLogger(__name__)


@extend_schema(tags=["Payments"])
class PaymentCreateView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CreatePaymentSerializer

    @extend_schema(
        request=CreatePaymentSerializer,
        responses={201: PaymentSerializer},
        summary="Create a payment",
        description="Requires X-Idempotency-Key header (UUID v4).",
    )
    def post(self, request):
        serializer = CreatePaymentSerializer(data=request.data)
        if not serializer.is_valid():
            return CustomResponse.validation_error(errors=serializer.errors, request=request)

        idempotency_key = request.META.get("HTTP_X_IDEMPOTENCY_KEY", "")
        ip = _get_ip(request)

        payment = PaymentService.create_payment(
            user=request.user,
            validated_data=serializer.validated_data,
            idempotency_key=idempotency_key,
            ip=ip,
        )

        return CustomResponse.success(
            message_key="PAYMENT_CREATED",
            request=request,
            data=PaymentSerializer(payment).data,
        )


@extend_schema(tags=["Payments"])
class PaymentDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrOwner]
    serializer_class = PaymentSerializer

    @extend_schema(responses={200: PaymentSerializer}, summary="Get payment by ID")
    def get(self, request, pk):
        payment = PaymentService.get_payment(payment_id=pk, user=request.user)
        self.check_object_permissions(request, payment)
        return CustomResponse.success(
            message_key="PAYMENT_FETCHED",
            request=request,
            data=PaymentSerializer(payment).data,
        )


@extend_schema(tags=["Payments"])
class PaymentListView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentListSerializer

    @extend_schema(
        responses={200: PaymentListSerializer(many=True)},
        parameters=[
            OpenApiParameter("page", int, description="Page number", default=1),
            OpenApiParameter("page_size", int, description="Items per page", default=20),
        ],
        summary="List user payments",
    )
    def get(self, request):
        page      = int(request.query_params.get("page", 1))
        page_size = min(int(request.query_params.get("page_size", 20)), 100)

        payments, total = PaymentService.list_payments(
            user=request.user, page=page, page_size=page_size
        )

        return CustomResponse.success(
            message_key="PAYMENT_LIST_FETCHED",
            request=request,
            data=PaymentListSerializer(payments, many=True).data,
            meta={
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size,
            },
        )


def _get_ip(request) -> str:
    x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded:
        return x_forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")
