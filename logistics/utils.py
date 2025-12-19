from .models import Order

def generate_custom_id():
    last_order = Order.objects.order_by('id').last()
    if not last_order or not last_order.id_number:
        return 'ST-8000'
    last_id = int(last_order.id_number.split('-')[1])
    return f"ST-{last_id + 1}"
