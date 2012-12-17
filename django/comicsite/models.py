import pdb

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.models import Group,Permission
from django.core.mail import send_mail
from django.db.models import get_app, get_models
from django.template import loader, Context
from django.template.loader import get_template


from django.utils.html import strip_tags



from userena.signals import signup_complete
from comicmodels.signals import new_admin

    
class ComicSiteException(Exception):
    """ any type of exception for which a django or python exception is not defined """
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)


# =============================== permissions ===================================
# put permissions code here because signal receiver code should go into models.py
# according to https://docs.djangoproject.com/en/dev/topics/signals/#connecting-receiver-functions
# TODO: where should this code go? This does not seem like a good place for permissions

def set_project_admin_permissions(sender, **kwargs):
    user = kwargs['user']
    
    # add this user to the projectadminsgroup, which means user can see and edit standard
    # objects types in admin.
    projectadmingroup = get_or_create_projectadmingroup()
    user.groups.add(projectadmingroup)
    
    # set staff status so user can access admin interface. User will still have to 
    # activate through email link before being able to log in at all.
    user.is_staff = True
    user.save()
                
    

def get_or_create_projectadmingroup():
    """ create the group 'projectadmin' which should have class-level permissions for all 
    models a project admin can edit. E.g. add/change/delete comicsite, page, 
    dropboxfolder. If group does not exists, recreate with default permissions.
    """
    (projectadmins,created) = Group.objects.get_or_create(name='projectadmins')
    
    if created:
        # if projectadmins group did not exist, add default permissions.
        # adding permissions to all models in the comicmodels app.
        appname = 'comicmodels'
        app = get_app(appname)
        for model in get_models(app):            
            classname = model.__name__.lower()            
            add_standard_perms(projectadmins,classname,appname)
        
    return projectadmins
    

def add_standard_perms(group,classname,app_label):
    """ convenience function to add add_classname,change_classname,delete_classname
    permissions to permissionsgroup group
    """
    
    can_add = Permission.objects.get(codename="add_"+classname, content_type__app_label=app_label)
    can_change = Permission.objects.get(codename="change_"+classname, 
                                        content_type__app_label=app_label)
    can_delete = Permission.objects.get(codename="delete_"+classname, 
                                        content_type__app_label=app_label)
    
    group.permissions.add(can_add,can_change,can_delete)
    

# when a user activates account, set permissions. dispatch_uid makes sure the receiver is only
# registered once.  see https://docs.djangoproject.com/en/dev/topics/signals/ 
signup_complete.connect(set_project_admin_permissions,dispatch_uid="set_project_\
                            admin_permissions_reveiver") 


# ======================================= sending notification emails ====================
def send_new_admin_notification_email(sender,**kwargs):
    
    comicsite = kwargs['comicsite']
    new_admin = kwargs['new_admin']
    site = kwargs['site']
    title = 'You are now admin for '+comicsite.short_name
    
    # maybe put this in try catch later. Leaving for now
    
    #template = get_template("admin/emails/new_admin_notification_email.txt")
    #message = template.render(Context(kwargs))
        
    #send_mail(title, message, "noreply@"+site.domain ,[new_admin.email], fail_silently=False)
    send_templated_email(title, "admin/emails/new_admin_notification_email.txt",kwargs,[new_admin.email]
                        ,"noreply@"+site.domain, fail_silently=False)
    
# connect to signal 
new_admin.connect(send_new_admin_notification_email,dispatch_uid='send_new_admin_notification_email')


def send_templated_email(subject, email_template_name, email_context, recipients, 
                        sender=None,bcc=None, fail_silently=True, files=None):
    
    """
    send_templated_mail() is a wrapper around Django's e-mail routines that
    allows us to easily send multipart (text/plain & text/html) e-mails using
    templates that are stored in the database. This lets the admin provide
    both a text and a HTML template for each message.

    email_template_name is the slug of the template to use for this message (see
        models.EmailTemplate)

    email_context is a dictionary to be used when rendering the template

    recipients can be either a string, eg 'a@b.com', or a list of strings.
    
    sender should contain a string, eg 'My Site <me@z.com>'. If you leave it
        blank, it'll use settings.DEFAULT_FROM_EMAIL as a fallback.

    bcc is an optional list of addresses that will receive this message as a
        blind carbon copy.

    fail_silently is passed to Django's mail routine. Set to 'True' to ignore
        any errors at send time.

    files can be a list of file paths to be attached, or it can be left blank.
        eg ('/tmp/file1.txt', '/tmp/image.png')

    """
   
    c = Context(email_context)
    if not sender:
        sender = settings.DEFAULT_FROM_EMAIL

    template = loader.get_template(email_template_name)
    
    text_part = strip_tags(template.render(c))
    html_part = template.render(c)
    
    if type(recipients) == str:
        if recipients.find(','):
            recipients = recipients.split(',')
    elif type(recipients) != list:
        recipients = [recipients,]
        
    msg = EmailMultiAlternatives(subject,
                                text_part,
                                sender,
                                recipients,
                                bcc=bcc)
    msg.attach_alternative(html_part, "text/html")

    if files:
        if type(files) != list:
            files = [files,]

        for file in files:
            msg.attach_file(file)

    return msg.send(fail_silently)
