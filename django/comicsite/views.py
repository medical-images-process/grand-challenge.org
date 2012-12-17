'''
Created on Jun 18, 2012

Testing views. Each of these views is referenced in urls.py 

@author: Sjoerd
'''
import pdb
import mimetypes

from django.contrib.admin.options import ModelAdmin
from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.http import HttpResponse,Http404
from django.shortcuts import render_to_response,get_object_or_404
from django.template import RequestContext,Context,Template,TemplateSyntaxError


from comicmodels.models import ComicSite,Page,ErrorPage,DropboxFolder
from comicsite.admin import ComicSiteAdmin
from comicsite.contextprocessors.contextprocessors import ComicSiteRequestContext
from comicsite.models import ComicSiteException
from comicsite.templatetags import template_tags

from dataproviders import FileSystemDataProvider


def index(request):
    return  HttpResponse("ComicSite index page.",context_instance=RequestContext(request))


def _register(request, site_short_name):
    """ Register the current user for given comicsite """
   
    #TODO: check whether user is allowed to register, maybe wait for verification,
    #send email to admins of new registration
        
    
    [site, pages, metafooterpages] = site_get_standard_vars(site_short_name)
    title = "registration successful"
   
    if request.user.is_authenticated():
        participantsgroup = Group.objects.get(name=site.participants_group_name())
        request.user.groups.add(participantsgroup)
        html = "<p> You are now registered to "+ site.short_name + "<p>"
        
    else:
        html = "you need to be logged in to use this url"
        
    currentpage = Page(comicsite=site,title=title,html=html)
    
    return render_to_response('page.html', {'site': site, 'currentpage': currentpage, "pages":pages},context_instance=RequestContext(request))
    
def site(request, site_short_name):
    """ Register the current user for the given comicsite """
   
    [site, pages, metafooterpages] = site_get_standard_vars(site_short_name)    
    
    if len(pages) == 0:
        page = ErrorPage(comicsite=site,title="no_pages_found",html="No pages found for this site. Please log in and use the admin button to add pages.")
        currentpage = page    
    else:
        currentpage = pages[0]
            
    currentpage = getRenderedPageIfAllowed(currentpage,request,site)
 
    #return render_to_response('page.html', {'site': site, 'currentpage': currentpage, "pages":pages, "metafooterpages":metafooterpages},context_instance=RequestContext(request))
    return render_to_response('page.html', {'site': site, 'currentpage': currentpage, "pages":pages},context_instance=RequestContext(request))

def site_get_standard_vars(site_short_name):
    """ When rendering a site you need to pass the current site, all pages for this site, and footer pages.
    Get all this info and return a dictionary ready to pass to render_to_response. Convenience method
    to save typing.
    """
    site = getSite(site_short_name)                    
    pages = getPages(site_short_name)        
    metafooterpages = getPages("COMIC")        
                
    return [site, pages, metafooterpages]
        
def concatdicts(d1,d2):
    return dict(d1, **d2)
    

def renderTags(request, p):
    """ render page contents using django template system
    This makes it possible to use tags like '{% dataset %}' in page 
    """
    
    rendererror = ""
    try:
        t = Template("{% load template_tags %}" + p.html)
    except TemplateSyntaxError as e:
        rendererror = e.message
    if (rendererror):
        # when page contents cannot be rendered, just display raw contents and include error message on page
        errormsg = "<span class=\"pageError\"> Error rendering template: " + rendererror + " </span>"
        pagecontents = p.html + errormsg
    else:
                
        #pass page to context here to be able to render tags based on which page does the rendering
        pagecontents = t.render(ComicSiteRequestContext(request,p))
        
    return pagecontents



def permissionMessage(request, site, p):
    if request.user.is_authenticated():
        msg = "You do not have permission to view page '" + p.title + "'. If you feel this is an error, please contact the project administrators"
        title = "No permission"
    else:
        msg = "The page '" + p.title + "' can only be viewed by registered users. Sign in to view this page."
        title = "Sign in required"
    page = ErrorPage(comicsite=site, title=title, html=msg)
    currentpage = page
    return currentpage


#TODO: could a decorator be better then all these ..IfAllowed pages?
def getRenderedPageIfAllowed(page_or_page_title,request,site):
    """ check permissions and render tags in page. If string title is given page is looked for 
        return nice message if not allowed to view"""
        
    if isinstance(page_or_page_title,unicode) or isinstance(page_or_page_title,str):
        page_title = page_or_page_title
        try:
            p = Page.objects.get(comicsite__short_name=site.short_name, title=page_title)
        except Page.DoesNotExist:                
            raise Http404
    else:
        p = page_or_page_title                
    
    if p.can_be_viewed_by(request.user):
        p.html = renderTags(request, p)
        currentpage = p
    else:
         
        currentpage = permissionMessage(request, site, p)
            
    return currentpage

    
def getPageSourceIfAllowed(page_title,request,site):
    """ check permissions and render tags in page. If string title is given page is looked for 
        return nice message if not allowed to view"""
    
    try:
        p = Page.objects.get(comicsite__short_name=site.short_name, title=page_title)
    except Page.DoesNotExist:
        raise Http404
        
    if p.can_be_viewed_by(request.user):        
        currentpage = p    

    else:         
        currentpage = permissionMessage(request, site, p)
            
    return currentpage



def page(request, site_short_name, page_title):
    """ show a single page on a site """
    
    [site, pages, metafooterpages] = site_get_standard_vars(site_short_name)
    
    currentpage = getRenderedPageIfAllowed(page_title,request,site)
        
    return render_to_response('page.html', {'site': site, 'currentpage': currentpage, "pages":pages, 
                                            "metafooterpages":metafooterpages},
                                            context_instance=RequestContext(request))


def pagesource(request, site_short_name, page_title):
    """ show the source html + tags of a a single page on a site """
    
    [site, pages, metafooterpages] = site_get_standard_vars(site_short_name)
    
    currentpage = getPageSourceIfAllowed(page_title,request,site)
    
    
    return render_to_response('pagesource.html', {'site': site, 'currentpage': currentpage, "pages":pages, 
                                            "metafooterpages":metafooterpages},
                                            context_instance=RequestContext(request))


def dropboxpage(request, site_short_name, page_title, dropboxname, dropboxpath):
    """ show contents of a file from dropbox account as page """
    
    (mimetype,encoding) = mimetypes.guess_type(dropboxpath)
    if mimetype.startswith("image"):
        return dropboximage(request, site_short_name, page_title,dropboxname, dropboxpath)
        
    [site, pages, metafooterpages] = site_get_standard_vars(site_short_name)
        
    p = get_object_or_404(Page,comicsite__short_name=site.short_name, title=page_title)
    
    baselink = reverse('comicsite.views.page', kwargs = {'site_short_name':p.comicsite.short_name, 'page_title':p.title})
    
    msg = "<div class=\"breadcrumbtrail\"> Displaying '"+dropboxpath+"' from dropboxfolder '"+dropboxname+"', originally linked from\
           page <a href=\""+baselink+"\">"+p.title+"</a> </div>"
    p.html = "{% dropbox title:"+dropboxname+" file:"+dropboxpath+" %} <br/><br/>" + msg

    currentpage = getRenderedPageIfAllowed(p,request,site)

        
    return render_to_response('dropboxpage.html', {'site': site, 'currentpage': currentpage, "pages":pages, 
                                            "metafooterpages":metafooterpages},
                                            context_instance=RequestContext(request))


def dropboximage(request, site_short_name, page_title,dropboxname,dropboxpath=""):
    """ Get image from dropbox and pipe through django. 
    Sjoerd: This method is probably very inefficient, however it works. optimize later > maybe get temp public link
    from dropbox api and let dropbox serve, or else do some cashing. Cut out the routing through django.
    """
    df = get_object_or_404(DropboxFolder,title=dropboxname)    
    provider = df.get_dropbox_data_provider()    
    (mimetype,encoding) = mimetypes.guess_type(dropboxpath)
    response = HttpResponse(provider.read(dropboxpath), content_type=mimetype)
    
    return response
    
    


def comicmain(request, page_title=""):
    """ show content as main page item. Loads pages from the 'comic' project """
    
    site_short_name = "comic"
    
    pages = getPages(site_short_name)
    
    #if no page title is given, just use the first page found 
    if page_title=="":        
        p = pages[0]    
        p.html = renderTags(request, p)
    else:    
        try:
            p = Page.objects.get(comicsite__short_name=site_short_name, title=page_title)
        except Page.DoesNotExist:                
            raise Http404
    
    
    p.html = renderTags(request, p)
    
    # render page contents using django template system
    # This makes it possible to use tags like '{% dataset %}' in page
    
    #to display pages from 'comic' project at the very bottom of the site
    metafooterpages = getPages("COMIC")
    
    return render_to_response('mainpage.html', {'site': p.comicsite, 'currentpage': p, "pages":pages, "metafooterpages":metafooterpages},context_instance=RequestContext(request))

                
    
def dataPage(request):
    """ test function for data provider. Just get some files from provider and show them as list"""
    #= r"D:\userdata\Sjoerd\Aptana Studio 3 Workspace\comic-django\django\static\files"
    
    path = r"D:\userdata\Sjoerd\Aptana Studio 3 Workspace\comic\comic-django\django\static\files"
    dp = FileSystemDataProvider.FileSystemDataProvider(path)
    images = dp.getImages()
    
    htmlOut = "available files:"+", ".join(images)
    p = createTestPage(html=htmlOut)
    
    pages = [p]
    
    return render_to_response('testpage.html', {'site': p.comicsite, 'currentpage': p, "pages":pages },context_instance=RequestContext(request))

# ======================================== not called directly from urls.py =========================================

def getSite(site_short_name):
    try:
        site = ComicSite.objects.get(short_name=site_short_name)
    except ComicSite.DoesNotExist:                
        raise Http404   
    return site  
    
def getPages(site_short_name):
    """ get all pages of the given site from db"""
    try:
        pages = Page.objects.filter(comicsite__short_name=site_short_name)
    except Page.DoesNotExist:                
        raise Http404
    return pages

# trying to follow pep 0008 here, finally.
def site_exists(site_short_name):
    try:
        site = ComicSite.objects.get(short_name=site_short_name)
        return True
    except ComicSite.DoesNotExist:                
        return False


def comic_site_to_html(comic_site):
     """ Return an html overview of the given ComicSite """
     link = reverse('comicsite.views.site', args=[comic_site.short_name])
     html = create_HTML_a(link,comic_site.short_name)
     
     if comic_site.description !="":
         html += " - " + comic_site.description
         
     img_html = create_HTML_a_img(link,comic_site.logo)
     
     html = "<table><tr valign=\"top\" ><td class = \"thumb\">" + img_html +"</td><td class = \"description\">"+ html + "</td></tr></table>"
     
     html = "<div class = \"comicSiteSummary\">" + html + "</div>"
     return html
    
def create_HTML_a(link_url,link_text):
    return "<a href=\"" + link_url + "\">" +  link_text + "</a>"


def create_HTML_a_img(link_url,image_url):
    """ create a linked image """
    img = "<img src=\"" + image_url + "\">"
    linked_image = create_HTML_a(link_url,img)    
    return linked_image
    
# ======================================================  debug and test ==================================================

 
def sendEmail(request):
    """Test email sending"""
    
    adress = 'sjoerdk@home.nl' 
    title = 'Your email setting are ok for sending'
    message = 'Just checking the sending of email using DJANGO. If you read this things are properly configured'
    
    
    send_mail(title, 'Here is the message.', 'from@example.com',
    [adress], fail_silently=False)
    text="Sent test email titled '" + title + "' to email adress '"+ adress +"'"
    
    return HttpResponse(text);
        

def createTestPage(title="testPage",html=""):
    """ Create a quick mockup on the ComicSite 'Test'"""
    
    if site_exists("test"):
        #TODO log a warning here, no exception.
        raise ComicSiteException("I am creating a spoof ComicSite called 'test' on the fly, by a project called 'test' was already defined in DB. This message should be a warning instead of an exception")                
    
    # if no site exists by that name, create it on the fly.
    site = ComicSite()
    site.short_name = "test"
    site.name = "Test Page"
    site.skin = ""
        
    return Page(comicsite=site,title=title,html=html)
    

def givePageHTML(page):
    return "<h1>%s</h1> <p>%s</p>" %(page.title ,page.html)