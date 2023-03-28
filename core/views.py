from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Profile,Post,LikePost,FollowersCount
from itertools import chain
import random
import cloudinary_storage
import cloudinary
import cloudinary.uploader
import cloudinary.api
from cloudinary.models import CloudinaryField
from cloudinary import CloudinaryImage
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url
from operator import attrgetter
from django.urls import reverse


def order_posts_by_created_at(posts):
    ordered_posts = sorted(posts, key=attrgetter('created_at'))
    return ordered_posts
def order_pic_by_created_at(pics):
    ordered_pics = sorted(pics, key=attrgetter('created_at'))
    return ordered_pics    




# Create your views here.
@login_required(login_url='signin')
def index(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)
    #intialise user_following_list with only the current user
    user_following_list = [request.user.username]
    feed = []

    user_following = FollowersCount.objects.filter(follower=request.user.username)

    for users in user_following:
        user_following_list.append(users.user)

    for usernames in user_following_list:
        feed_lists = Post.objects.filter(user=usernames)
        feed.append(feed_lists)
        

    feed_list = list(chain(*feed))
    feed_list = sorted(feed_list, key=attrgetter('created_at'))

    # user suggestion starts
    all_users = User.objects.all()
    user_following_all = []

    for user in user_following:
        user_list = User.objects.get(username=user.user)
        user_following_all.append(user_list)
    
    new_suggestions_list = [x for x in list(all_users) if (x not in list(user_following_all))]
    current_user = User.objects.filter(username=request.user.username)
    final_suggestions_list = [x for x in list(new_suggestions_list) if ( x not in list(current_user))]
    random.shuffle(final_suggestions_list)
    # i want also to add the user profile to the suggestion list
    

    username_profile = []
    username_profile_list = []
    
    for users in final_suggestions_list:
        username_profile.append(users.id)

    for ids in username_profile:
        profile_lists = Profile.objects.filter(id_user=ids)
        username_profile_list.append(profile_lists)
    # i want aslo to see my owen poston the feed



    suggestions_username_profile_list = list(chain(*username_profile_list))
    




    return render(request, 'index.html', {'user_profile': user_profile, 'posts':feed_list, 'suggestions_username_profile_list': suggestions_username_profile_list[:4]})



@login_required(login_url='signin')
def settings(request):
    user_profile = Profile.objects.get(user=request.user)
    user= User.objects.get(username=request.user.username)

    if request.method == 'POST':
        
        if request.FILES.get('image') == None:
            image = user_profile.profileimg
            bio = request.POST['bio']
            location = request.POST['location']
            email = request.POST['email']
            # take the email and change the first letter into small letter 
            

            

            user_profile.profileimg = image
            user_profile.bio = bio
            if User.objects.filter(email=email).exists() or User.objects.filter(email=email.lower()).exists() or User.objects.filter(email=email.capitalize()).exists():
                messages.info(request, 'Email Taken')
            else:
                user.email = email
                user.save()

    
            user_profile.location = location
            user_profile.save()
        if request.FILES.get('image') != None:
            image = request.FILES.get('image')
            bio = request.POST['bio']
            email = request.POST['email']
            location = request.POST['location']
            if User.objects.filter(email=email).exists():
                    messages.info(request, 'Email Taken')
                
            else:
                user.email = email
                user.save()
            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()

        
        return redirect('settings')
    return render(request, 'setting.html', {'user_profile': user_profile})

def signup(request):

    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if len(password) < 8:
                messages.info(request, 'Password must be at least 8 characters')
                return redirect('signup')
            if User.objects.filter(email=email).exists() or User.objects.filter(email=email.lower()).exists() or User.objects.filter(email=email.capitalize()).exists():
                messages.info(request, 'Email Taken')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username Taken')
                return redirect('signup')
            elif len(username) < 4:
                messages.info(request, 'Username must be at least 4 characters')
                return redirect('signup')
            elif len(username) > 8:
                messages.info(request, 'Username must be less than 9 characters')
                return redirect('signup')        
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                user_login=auth.authenticate(username=username, password=password)

                auth.login(request, user_login)
                

                #create a Profile object for the new user
                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
                new_profile.save()
                return redirect('settings')
                
        else:
            messages.info(request, 'Password Not Matching')
            return redirect('signup')
        
    else:
        return render(request, 'signup.html')

def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('/') # redirect to home page
        else:
            messages.info(request, 'Invalid Credentials')
            return redirect('signin')
        
    else:
        return render(request, 'signin.html')

@login_required(login_url='signin')
def logout(request):

    auth.logout(request)
    return redirect('signin')


@login_required(login_url='signin')
def upload(request):

    if request.method == 'POST':
        user = request.user.username
        #check if user has uploaded an image
        if request.FILES.get('image_upload')!= None:
            image = request.FILES.get('image_upload')
        else:
            #if user has not uploaded an image, use the default image
            image = 'default.jpg'

        caption = request.POST['caption']

        new_post = Post.objects.create(user=user, image=image, caption=caption)
        new_post.save()

        return redirect('/')
    else:
        return redirect('/')



@login_required(login_url='signin')
def like_post(request):
    username = request.user.username
    post_id = request.GET.get('post_id')

    post = Post.objects.get(id=post_id)

    like_filter = LikePost.objects.filter(post_id=post_id, username=username).first()

    if like_filter == None:
        new_like = LikePost.objects.create(post_id=post_id, username=username)
        new_like.save()
        post.no_of_likes = post.no_of_likes+1
        post.save()
        return redirect('/')
    else:
        like_filter.delete()
        post.no_of_likes = post.no_of_likes-1
        post.save()
        return redirect('/')


@login_required(login_url='signin')
def profile(request, pk):
    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
    user_posts = Post.objects.filter(user=pk)
    user_posts=order_pic_by_created_at(user_posts)
    user_post_length = len(user_posts)

    follower = request.user.username
    user = pk

    if FollowersCount.objects.filter(follower=follower, user=user).first():
        button_text = 'Unfollow'
    else:
        button_text = 'Follow'

    user_followers = len(FollowersCount.objects.filter(user=pk))
    user_following = len(FollowersCount.objects.filter(follower=pk))

    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_post_length': user_post_length,
        'button_text': button_text,
        'user_followers': user_followers,
        'user_following': user_following,
    }
    return render(request, 'profile.html', context)


@login_required(login_url='signin')
def follow(request):
    if request.method == 'POST':
        follower = request.POST['follower']
        user = request.POST['user']

        if FollowersCount.objects.filter(follower=follower, user=user).first():
            delete_follower = FollowersCount.objects.get(follower=follower, user=user)
            delete_follower.delete()
            return redirect('/profile/'+user)
        else:
            new_follower = FollowersCount.objects.create(follower=follower, user=user)
            new_follower.save()
            return redirect('/profile/'+user)
    else:
        return redirect('/')    
        


@login_required(login_url='signin')
def search(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    if request.method == 'POST':
        username = request.POST['username']
        username_object = User.objects.filter(username__icontains=username)

        username_profile = []
        username_profile_list = []

        for users in username_object:
            username_profile.append(users.id)

        for ids in username_profile:
            profile_lists = Profile.objects.filter(id_user=ids)
            username_profile_list.append(profile_lists)
        
        username_profile_list = list(chain(*username_profile_list))
    return render(request, 'search.html', {'user_profile': user_profile, 'username_profile_list': username_profile_list})    




@login_required(login_url='signin')
def gotoprofile(request):
    return redirect('/profile/'+request.user.username)



def testhome(request):
    return render(request, 'testhome.html')


    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
    user_posts = Post.objects.filter(user=pk)
    user_post_length = len(user_posts)

    follower = request.user.username
    user = pk

    if FollowersCount.objects.filter(follower=follower, user=user).first():
        button_text = 'Unfollow'
    else:
        button_text = 'Follow'

    user_followers = len(FollowersCount.objects.filter(user=pk))
    user_following = len(FollowersCount.objects.filter(follower=pk))

    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_post_length': user_post_length,
        'button_text': button_text,
        'user_followers': user_followers,
        'user_following': user_following,
    }
    return render(request, 'testprofile.html', context)    


@login_required(login_url='signin')
def removepost(request):
    if request.method == 'POST':
        post_id = request.POST['post_id']
        post = Post.objects.get(id=post_id)
        post.delete()
        return redirect('/')
    else:
        return redirect('/')








