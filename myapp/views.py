from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.views.generic import CreateView,View,TemplateView,FormView,UpdateView,ListView,DeleteView,DetailView
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth import authenticate,login,logout
from django.db.models import Q
from django.utils.decorators import method_decorator

from myapp.forms import SignUpForm,SignInForm,ProfileEditForm,PostForm,CoverpicForm,ProfilepicChangeForm
from myapp.models import UserProfile,Posts,Comments

def sign_required(fn):
    def wrapper(request,*args,**kwargs):
        if not request.user.is_authenticated:
            messages.error(request,'Please Login')
            return redirect('login')
        return fn(request,*args,**kwargs)
    return wrapper

class SignUpView(CreateView):
    model=User
    form_class=SignUpForm
    template_name="register.html"
    success_url=reverse_lazy("login")

    def form_valid(self, form):
        messages.success(self.request,"Account has been created")
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request,"Failed to create account")
        return super().form_invalid(form)

class SignInView(FormView):
    model=User
    form_class=SignInForm
    template_name="login.html"

    # def get(self,request,*args,**kwargs):
    #     form=self.form_class
    #     return render(request,self.template_name,{"form":form})
    
    def post(self,request,*args,**kwargs):
        form=self.form_class(request.POST)
        if form.is_valid():
            uname=form.cleaned_data.get("username")
            pwd=form.cleaned_data.get("password")
            usr=authenticate(request,username=uname,password=pwd)
            print('hello')
            if usr:
                login(request,usr)
                messages.success(request,"login successfully")
                return redirect("index")
            messages.error(request,"login failed")
        return render(request,self.template_name,{"form":form})

@method_decorator(sign_required,name='dispatch')   
class IndexView(CreateView,ListView):
    template_name="index.html"
    form_class=PostForm
    model=Posts
    context_object_name="posts"
    success_url=reverse_lazy("index")
    def form_valid(self, form):
        form.instance.user=self.request.user
        return super().form_valid(form)


@method_decorator(sign_required,name='dispatch')
class ProfileEditView(UpdateView):

    model=UserProfile
    form_class=ProfileEditForm
    template_name="profile-edit.html"
    success_url=reverse_lazy("index")

    def form_valid(self, form):
        messages.success(self.request,"Updated")
        return super().form_valid(form)

@sign_required    
def signout_view(request,*args,**kwargs):
    logout(request)
    return redirect('login')

#localhost:8000/posts/{id}/like/
@sign_required
def add_like_view(request,*args,**kwargs):
    id=kwargs.get("pk")
    post_obj=Posts.objects.get(id=id)
    post_obj.liked_by.add(request.user)
    return redirect('index')

#localhost:8000/posts/{id}/comment/add/
@sign_required
def add_comment_view(request,*args,**kwargs):
    id=kwargs.get('pk')
    post_obj=Posts.objects.get(id=id)
    comment=request.POST.get('comment')
    Comments.objects.create(user=request.user,post=post_obj,comment_text=comment)
    return redirect('index')

#localhost:8000/comments/{id}/remove/
@sign_required
def comment_remove_view(request,*args,**kwargs):
    id=kwargs.get("pk")
    comment_obj=Comments.objects.get(id=id)
    if request.user == comment_obj.user:
        comment_obj.delete()
        return redirect('index')
    else:
        messages.error(request,"please contact admin")
        return redirect('login')

@method_decorator(sign_required,name='dispatch')   
class ProfileDetailview(DetailView):
    model=UserProfile
    template_name="profiledet.html"
    context_object_name="profile"

#localhost:8000/profile/{id}/coverpic/change
@sign_required
def coverpic_Change_View(request,*args,**kwargs):
    id=kwargs.get("pk")
    prof_obj=UserProfile.objects.get(id=id)
    form=CoverpicForm(instance=prof_obj,data=request.POST,files=request.FILES)
    if form.is_valid():
        form.save()
        return redirect("profile-detail",pk=id)
    return redirect('profile-detail',pk=id)

#localhost:8000/profile/{id}/profilepic/change/
@sign_required
def profilepic_change_view(request,*args,**kwargs):
    id=kwargs.get('pk')
    prof_obj=UserProfile.objects.get(id=id)
    form=ProfilepicChangeForm(instance=prof_obj,data=request.POST,files=request.FILES)
    if form.is_valid():
        form.save()
        return redirect('profile-detail',pk=id)

#localhost:8000/profiles/all/
@method_decorator(sign_required,name='dispatch')  
class ProfileListView(ListView):
    model=UserProfile
    template_name="profile-list.html"
    context_object_name="profiles"
   
    def get_queryset(self):
        return UserProfile.objects.exclude(user=self.request.user)
    
    def post(self,request,*args,**kwargs):
        pname=request.POST.get('username')
        qs=UserProfile.objects.filter(Q(user__username__icontains=pname) | Q(user__first_name__icontains=pname) | Q(user__last_name__icontains=pname))
        messages.error(request,'invalid')
        return render(request,self.template_name,{"profiles":qs})
    

#localhost:8000/profiles/{id}/follow/
@sign_required
def follow_view(request,*args,**kwargs):
    id=kwargs.get('pk')
    prof_obj=UserProfile.objects.get(id=id)
    user_prof=request.user.profile
    user_prof.following.add(prof_obj)
    user_prof.save()
    return redirect('index')    

#localhost:8000/profiles/{id}/unfollow/
@sign_required
def unfollow_view(request,*args,**kwargs):
    id=kwargs.get('pk')
    prof_obj=UserProfile.objects.get(id=id)
    user_prof=request.user.profile
    user_prof.following.remove(prof_obj)
    user_prof.save()
    return redirect('index')

@sign_required
def post_delete_view(request,*args,**kwargs):
    post_id=kwargs.get("pk")
    post_obj=Posts.objects.get(id=post_id)
    post_obj.delete()
    return redirect('index')   
    






    

    


        

