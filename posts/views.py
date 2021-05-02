from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from .models import Post, Like
from profiles.models import Profile
from .forms import PostModelForm, CommentModelForm
from django.views.generic import UpdateView, DeleteView
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView, DeleteView
from django.contrib import messages
# Create your views here.


def post_comment_create_and_list_view(request):
    qs = Post.objects.all()
    profile = Profile.objects.get(user=request.user)


    context = {
        'qs': qs,
        'profile': profile,
    }

    return render(request, 'posts/main.html', context)


def like_unlike_post(request):
    user = request.user

    if request.method == "POST":
        post_id  = request.POST.get('post_id')
        post_obj = Post.objects.get(id=post_id)
        profile  = Profile.objects.get(user=user)
        
        if profile in post_obj.liked.all():
            post_obj.liked.remove(profile)
        else:
            post_obj.liked.add(profile)

        like, created = Like.objects.get_or_create(user=profile, post_id=post_id)

        if not created:
            if like.value == 'Like':
                like.value = 'Unlike'
            else:
                like.value = 'Like'
            
            post_obj.save()

            like.save()
        data = {
            'value': like.value,
            'likes': post_obj.liked.all().count()
        }

        return JsonResponse(data, safe=False)

    return redirect('posts:main-post-view')


class PostDeleteView(DeleteView):
    model = Post 
    template_name= 'posts/confirm_del.html'
    success_url= reverse_lazy('posts:main-post-view')
    # success_url= '/posts/'
    
    def get_object(self, *args, **kwargs):
        pk = self.kwargs.get('pk')
        obj = Post.objects.get(pk=pk)
        if not obj.author.user == self.request.user:
            messages.warning(self.request, 'You must be the author of the post to be able to delete it!')
        return obj


class PostUpdateView(UpdateView):
    form_class = PostModelForm
    model = Post 
    template_name = 'posts/update.html'
    success_url= reverse_lazy('posts:main-post-view')
    
    def form_valid(self, form):
        profile = Profile.objects.get(user=self.request.user) 
        if form.instance.author == profile:
            return super().form_valid(form)
        else:
            form.add_error(None, 'You must be the author of the post to be able to update it!')
            return super().form_invalid(form)
