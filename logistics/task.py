from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_contact_email(self, mail,name,number,message):
    body = f'''
You have received a new message from the contact form:

Name: { name }
Phone Number: { number }
Email: { mail }

Message:
{ message }

--------------------------
Sent via your website's contact form.


        '''
    try:
        subject = "A Quote Request"
        message =body
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [mail]

        send_mail(subject, message, from_email, recipient_list)

        return f"Email sent to {from_email}"
    except Exception as e:
        # Retry the task if something fails (like connection issues)
        raise self.retry(exc=e)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_quote_email(self, mail, Customername, itemname, service, pick, dest, No_items):
    body = f'''
Dear {Customername},

Thank you for requesting a quote with us. Based on the details you provided, here is your tailored quote:

Total Quote: ₦[Total Amount]

Service Details:

Service Type: {service}

Item Name: {itemname}

Quantity of Item: {No_items}

Destination: from { pick}--{dest}

Pickup Contact Number: number


This quote is valid for the next [10 days]. Delivery is scheduled within [10 working days] from pickup once payment is confirmed.

If you’d like to proceed or have any questions, just reply to this email. We’re ready to assist you every step of the way.

Best regards,
Springtide Logistics

Customer Service Team      

        '''
    try:
        subject = "A Quote Request"
        message =body
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [mail]

        send_mail(subject, message, from_email, recipient_list)

        return f"Email sent to {from_email}"
    except Exception as e:
        # Retry the task if something fails (like connection issues)
        raise self.retry(exc=e)



@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def register_mail(self,mail,lastname,firstname,role):
    body =f'''
Dear {lastname} {firstname},

Welcome to SpringTide Logistics!

You have been successfully registered as a {role} on our platform.  
We’re excited to have you on board.




You can now log in and start using the platform to manage your deliveries, track shipments, or assist customers — depending on your assigned role.

If you have any questions, feel free to reach out to the support team.

Best regards,  
SpringTide Logistics  
Billing & Accounts Team
        '''
    

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def invoice_generate(self,mail,name,amount,issue_date,due_date,id):
        body = f'''
Here is your invoice (ID: {id}) from SpringTide Logistics.        
  Dear {name},

        Thank you for doing business with SpringTide Logistics.

        Please find below the details of your invoice:

        Amount Due: £{amount}
        Issue Date: {issue_date}
        Due Date: {due_date}

        Kindly ensure payment is made on or before the due date.

        If you have any questions or need assistance, feel free to reply to this email.

        Best regards,  
        SpringTide Logistics Billing Team
        """

        '''

        try:
            subject = "Invoice Notification"
            message =body
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [mail]

            send_mail(subject, message, from_email, recipient_list)

            return f"Invoice has been  sent successfully!!!"
        except Exception as e:
        # Retry the task if something fails (like connection issues)
            raise self.retry(exc=e)


    





