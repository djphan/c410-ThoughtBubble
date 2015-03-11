import calendar
from datetime import timedelta
import random

from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.models import Count
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404, render_to_response
from django.template import RequestContext, loader
from django.core.context_processors import csrf

import uuid
import Post
import Comment

from main.models import Authors, Friends, Posts, Comments, GithubStreams, TwitterStreams, FacebookStreams
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout as auth_logout

import json

def indexPage(request):
    context = RequestContext(request)

    return render(request, 'index/intro.html', request.session)

def redirectIndex(request):
    return redirect(indexPage)
    
def mainPage(request, current_user):
    context = RequestContext(request)
    error_msg = "Not Logged In. Please Login Here."

    if request.user.is_authenticated():
        current_user = request.user.get_username()
        author_name = Authors.objects.get(username=current_user)
    
        items = []
        if request.method == "GET":
            for x in Posts.objects.all().order_by("date"):
               items.insert(0,x)
	 
            return render(request,'main.html',{'items':items})
    
    else:
        return render(request, 'login.html', {'error_msg':error_msg})
        

def loginPage(request):

    if request.method == "POST":

        # Handle if signin not clicked
        if len(request.POST) == 0:
            return render(request, 'login.html')

        username = request.POST.get('username', "").strip()
        password = request.POST.get('password', "").strip()
        error_msg = None

        # Check if fields are filled.
        if username and password:

            user = authenticate(username=username, password=password)
            # Determine if user exists.
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect(mainPage, current_user=request.user.get_username())

                    """
                    This is an attempt to get sessions up. HALP.

                    author = Authors.objects.get(username=username, 
                            location='bubble')
                    author_dict = {'authors' : author}



                    response = render_to_response("main.html", author_dict, context)             
                    return response

                    try:        

                        template = loader.get_template('main.html')
                        context = RequestContext(request, request.session)

                        return HttpResponse(template.render(context))

                    
                        data = json.dumps({
                                'author_uuid' : author.__dict__['author_uuid'],
                                'username': username })
                        return HttpResponse(data, content_type='application/json')
                    

                    except (KeyError, Authors.DoesNotExist):

                        request.session['author_uuid'] = None
                        request.session['username'] = None
                        logout(request)

                        error_msg = "Cannot store session information." 
                        return render (request, 'login.html', {'error_msg':error_msg })
                    """


                else:
                    error_msg = """Account is deactivated. Please contact 
                                website hosts for further assistance."""

                    return render (request, 'login.html', {'error_msg':error_msg })

            else:
                error_msg = "Username or password is not valid. Please try again." 
                return render (request, 'login.html', {'error_msg':error_msg })


        else:
            error = "Missing either a username or password. Please supply one "

        error_msg = error_msg if error else "Unknown Error."
        return render(request, 'login.html', {'error_msg': error_msg})

    else:
        return render(request, 'login.html')

def logout(request):
    context = RequestContext(request)
    auth_logout(request)
    return redirect(indexPage)

# TODO: use profile template to load page of FOAF
def foaf(request,userid1=None,userid2=None):
	# we want to check if userid1 is friends with/is current user then check if 
	# userid1 is friends with userid2.. if so load userid2's profile so they can be friended?
	current_user = request.user
	user1 = Authors.objects.get(userid=userid1)
	print user1
	print user2
	user2 = Authors.objects.get(userid=userid2)
	inviter = Friends.objects.get(userid1=inviter_id_id)
	items = []
	# if logged in
	#if request.user.is_authenticated():
		# for e in Friends.objects.filter(invitee_id_id=user1): 
		# 	if Friends.objects.filter(inviter_id_id = user2) and e.status = True:
		# 		a = Authors.objects.filter(author_id=user2)
		# 		items.append(a)
        	
  #       for e in Friends.objects.filter(inviter_id_id=user1): 
  #           if Friends.objects.filter(invitee_id_id=user2) and e.status = True:
  #           	a = Authors.objects.filter(author_id=user2)
  #           	items.append(a)
	# foaf.html should be a profile page of userid2 ie: service/author/userid2 when that's working
	return render(request, 'foaf.html',{'items':items})
  

def friendRequest(request):
    items = []
    current_user = request.user
    if request.method == 'GET':
        print current_user.id
        #print request.user.is_authenticated()

        # if logged in
        if request.user.is_authenticated():

            for e in Friends.objects.filter(invitee_id_id=current_user.id): 
                if e.status is False :
                    a = Authors.objects.filter(author_id=e.inviter_id_id)
                    items.append(a)
        else: #do it anyway for now using ID 4 even if not logged in
        # ex: 4 has asked 3 to be their friend.
        # 	  2 has asked 3 to be their friend. Show 2 and 4 as followers of 3
            for e in Friends.objects.filter(invitee_id_id=3): 
                if e.status is False :
                    a = Authors.objects.filter(author_id=e.inviter_id_id)
                    items.append(a)
    if request.method == 'POST':
    	userid = current_user.id

    return render(request, 'friendrequest.html',{'items':items})

def friends(request):
    items = []
    if request.method == 'GET':
        current_user = request.user
        print current_user.id
        #print request.user.is_authenticated()

        # if logged in
        if request.user.is_authenticated():
            for e in Friends.objects.filter(inviter_id_id=current_user.id): 
                if e.status is True :
                    a = Authors.objects.filter(author_id=e.invitee_id_id)
                    items.append(a)
                #print a.values('name')

            for e in Friends.objects.filter(invitee_id_id=current_user.id): 
                if e.status is True :
                    a = Authors.objects.filter(author_id=e.inviter_id_id)
                    items.append(a)
        else: #do it anyway for now using ID 1 even if not logged in
            for e in Friends.objects.filter(inviter_id_id=1): 
                if e.status is True:
                    a = Authors.objects.filter(author_id=e.invitee_id_id)
                    items.append(a)

            for e in Friends.objects.filter(invitee_id_id=1): 
                if e.status is True :
                    a = Authors.objects.filter(author_id=e.inviter_id_id)
                    items.append(a)

    if request.method == 'POST':
        current_user = request.user
        searchField = request.POST.get("searchuser","")
        print searchField
        if request.user.is_authenticated():
            if searchField != "":
                for e in Friends.objects.filter(inviter_id_id=current_user.id):
                    if e.status is True :
                        a = Authors.objects.filter(name=searchField)
                        if a.exists():
                            items.append(a)
            #print a.values('name')

    return render(request, 'friends.html',{'items':items})


def profileMain(request):
    items = []
    if request.method == 'GET':
        current_user = request.user
        #print current_user.id
        #print request.user.is_authenticated()
        
        # if logged in
        if request.user.is_authenticated():
            for e in Friends.objects.filter(inviter_id_id=current_user.id):
                if e.status is True :
                    a = Authors.objects.filter(author_id=e.invitee_id_id)
                    items.append(a)
            #print a.values('name')
            
            for e in Friends.objects.filter(invitee_id_id=current_user.id):
                if e.status is True :
                    a = Authors.objects.filter(author_id=e.inviter_id_id)
                    items.append(a)
        else: #do it anyway for now using ID 1 even if not logged in
            for e in Friends.objects.filter(inviter_id_id=1):
                if e.status is True:
                    a = Authors.objects.filter(author_id=e.invitee_id_id)
                    items.append(a)
        
            for e in Friends.objects.filter(invitee_id_id=1):
                if e.status is True :
                    a = Authors.objects.filter(author_id=e.inviter_id_id)
                    items.append(a)

    return render(request, 'profile.html',{'items':items})



def getyourProfile(request, current_user):

    items = []
    ufriends=[]
    if request.method == "GET":
        
        if request.user.is_authenticated(): 
            current_user = request.user.username       

            yourprofileobj = Authors.objects.get(username=current_user, location="bubble")
            items.append(yourprofileobj)
            """
            for e in Friends.objects.filter(inviter_id_id=current_user.id):
                if e.status is True :
                    a = Authors.objects.filter(author_id=e.invitee_id_id)
                    ufriends.append(a)
                        #print a.values('name')

            for e in Friends.objects.filter(invitee_id_id=current_user.id):
                if e.status is True :
                    a = Authors.objects.filter(author_id=e.inviter_id_id)
                    ufriends.append(a)
        else: #do it anyway for now using ID 1 even if not logged in
            for e in Friends.objects.filter(inviter_id_id=1):
                if e.status is True:
                    a = Authors.objects.filter(author_id=e.invitee_id_id)
                    ufriends.append(a)
        
            for e in Friends.objects.filter(invitee_id_id=1):
                if e.status is True :
                    a = Authors.objects.filter(author_id=e.inviter_id_id)
                    ufriends.append(a)


        return render(request,'profile.html',{'items':items},{'ufriends':ufriends})
        """
        return render(request,'profile.html',{'items':items})


def getaProfile(request, user_id):
    items = []
    uFriends = []
    if request.method =="GET":
        user = Authors.objects.get(author_uuid=user_id, location="bubble")
        items.append(user)

        for e in Friends.objects.filter(inviter_id_id=user.author_id):
            if e.status is True :
                a = Authors.objects.filter(author_id=e.invitee_id_id)
                ufriends.append(a)
        #print a.values('name')

        for e in Friends.objects.filter(invitee_id_id=user.author_id):
            if e.status is True :
                a = Authors.objects.filter(author_id=e.inviter_id_id)
                ufriends.append(a) 

        return render(request,'profile.html',{'items':items,'ufriends':uFriends})

    if request.method == "POST":
        user = request.POST["username"]

        yourprofileobj = Authors.objects.get(username=user, location="bubble")
        items.append(yourprofileobj)

        for e in Friends.objects.filter(inviter_id_id=yourprofileobj.author_id):
            if e.status is True :
                a = Authors.objects.filter(author_id=e.invitee_id_id)
                ufriends.append(a)
        #print a.values('name')

        for e in Friends.objects.filter(invitee_id_id=yourprofileobj.author_id):
            if e.status is True :
                a = Authors.objects.filter(author_id=e.inviter_id_id)
                ufriends.append(a)
        
        return render(request,'profile.html',{'items':items,'ufriends':uFriends})
            
    #return render(request,'profile.html',{'items':items})



def editProfile(request, current_user):
    return render(request, 'Editprofile.html')

def makePost(request):
    if request.method == "POST":
        
        current_user = request.user.username
        
        author_id = Authors.objects.get(username=current_user)
        
        content = request.POST["posttext"]
        privacy = "public"
            #author_id = "heyimcameron"
      
        try:
            image=request.FILES["image"]
        except:
            image=""
        

        new_post = Posts.objects.get_or_create(author_id = author_id,content = content, image=image, privacy = privacy )

        return redirect(mainPage, current_user=request.user.username)

def registerPage(request):
    if request.method == 'POST':

        #print request
        error_msg = None
        success = None

        name=request.POST.get("name", "")
        username=request.POST["username"]
        password=request.POST["password"]
        email=request.POST.get("email", "")
        github=request.POST.get("github", "")
        facebook=request.POST.get("facebook", "")
        twitter=request.POST.get("twitter", "")
        location="bubble"

        try:
            image=request.FILES["image"]
        except:
            image=""

        if Authors.objects.filter(username=username):
            error_msg = "Username already exists"
            return render (request, 'Register.html', {'error_msg':error_msg, 'name':name, 'username':username, 'email':email, 'image':image, 'github':github, 'facebook':facebook, 'twitter':twitter})

        if Authors.objects.filter(email=email):
            error_msg = "Email already exists"
            return render (request, 'Register.html', {'error_msg':error_msg, 'name':name, 'username':username, 'email':email, 'github':github, 'facebook':facebook, 'twitter':twitter})
           
        new_user = User.objects.create_user(username, email, password)
        new_author = Authors.objects.get_or_create(name=name, username=username, 
            image=image, location=location, email=email, github=github, 
            facebook=facebook, twitter=twitter)

        # Successful. Redirect to Login
        success = "Registration complete. Please sign in."
        return HttpResponseRedirect("/main/login", {"success": success})

    else:
        
        # Render Register Page
        return render(request, 'Register.html')

def searchPage(request):
    items = []
    if request.method == 'POST':
        #searchField = request.POST["searchuser"]
        current_user = request.user
        print current_user.id
        #print request.user.is_authenticated()
        
        # if logged in
        if request.user.is_authenticated():
            for e in Friends.objects.filter(inviter_id_id=current_user.id):
                if e.status is True :
                    a = Authors.objects.filter(author_id=e.invitee_id_id)
                    items.append(a)
            #print a.values('name')
            
            for e in Friends.objects.filter(invitee_id_id=current_user.id):
                if e.status is True :
                    a = Authors.objects.filter(author_id=e.inviter_id_id)
                    items.append(a)
        else: #do it anyway for now using ID 1 even if not logged in
            for e in Friends.objects.filter(inviter_id_id=1):
                if e.status is True:
                    a = Authors.objects.filter(author_id=e.invitee_id_id)
                    items.append(a)
        
            for e in Friends.objects.filter(invitee_id_id=1):
                if e.status is True :
                    a = Authors.objects.filter(author_id=e.inviter_id_id)
                    items.append(a)

    return render(request, 'search.html',{'items':items})
      
