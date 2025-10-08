from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect

from a_rtchat.forms import ChatMessageCreateForm, NewGroupForm, ChatRoomEditForm
from a_rtchat.models import *



# Create your views here.
@login_required
def chat_view(request, chatroom_name='gang-gang' ):
    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)
    chat_messages = chat_group.chat_messages.all()[:30]
    form = ChatMessageCreateForm()

    #private chat
    other_user = None
    if chat_group.is_private:
        if request.user not in chat_group.members.all():
            raise Http404()
        other_user = chat_group.members.exclude(id=request.user.id).first()
        for member in chat_group.members.all():
            if member != request.user:
                other_user = member
                break

    if chat_group.group_name:
        if request.user not in chat_group.members.all():
            if request.user.emailaddress_set.filter(verified=True).exists():
                chat_group.members.add(request.user)
            else:
                messages.warning(request, 'Verify email to join the chat')
                return redirect('profile-settings')

    if request.htmx:
        form = ChatMessageCreateForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.author = request.user
            message.group = chat_group
            message.save()
            context = {
                'message': message,
                'user': request.user,

            }
            return render(request, 'partials/chat_message_p.html', context)

    context = {
        'chat_messages': chat_messages,
        'form': form,
        'other_user': other_user,
        'chatroom_name': chatroom_name,
        'chat_group': chat_group,
    }

    return render(request, 'chat.html', context)


@login_required
def get_or_create_chatroom(request, username):
    if request.user.username == username:
        return redirect('home')

    other_user = User.objects.get(username=username)
    my_chatrooms = request.user.chat_groups.filter(is_private=True)

    chatroom = None
    if my_chatrooms.exists():
        for c in my_chatrooms:
            if other_user in c.members.all():
                chatroom = c
                break
    if not chatroom:
        chatroom = ChatGroup.objects.create(is_private=True)
        chatroom.members.add(other_user, request.user)

    return redirect('chatroom', chatroom_name=chatroom.group_name)


@login_required
def create_groupchat(request):
    form = NewGroupForm()

    #save data to database
    if request.method == 'POST':
        form = NewGroupForm(request.POST)
        if form.is_valid():
            new_groupchat = form.save(commit=False)
            new_groupchat.admin = request.user
            new_groupchat.save()
            new_groupchat.members.add(request.user)
            return redirect('chatroom', new_groupchat.group_name)

    context = {
        'form': form,
    }
    return render(request, 'create_groupchat.html', context)

@login_required
def chatroom_edit_view(request, chatroom_name):
    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)
    if request.user != chat_group.admin:
        raise Http404()

    form = ChatMessageCreateForm(instance=chat_group)

    if request.method == 'POST':
        form = ChatRoomEditForm(request.POST, instance=chat_group)
        if form.is_valid():
            form.save()

            remove_members = request.POST.getlist('remove_members')
            for member_id in remove_members:
                member = User.objects.get(id=member_id)
                chat_group.members.remove(member)
            return redirect('chatroom', chatroom_name)

    context = {
        'form': form,
        'chat_group': chat_group,
    }
    return render(request, 'chatroom_edit.html', context)


@login_required
def chatroom_delete_view(request, chatroom_name):
    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)
    if request.user != chat_group.admin:
        raise Http404()

    if request.method == 'POST':
        chat_group.delete()
        messages.success(request, 'Chat group deleted')
        return redirect('home')
    return render(request, 'chatroom_delete.html', {'chat_group': chat_group})


@login_required
def chatroom_leave_view(request, chatroom_name):
    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)
    if request.user not in chat_group.members.all():
        raise Http404()

    if request.method == 'POST':
        chat_group.members.remove(request.user)
        messages.success(request, 'You left the chat')
        return redirect('home')


    messages.error(request, 'Invalid request. Please confirm leaving through the form.')
    return redirect('home')








