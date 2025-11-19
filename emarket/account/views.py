from datetime import datetime, timedelta
from django.utils import timezone
from django.shortcuts import  get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from .serializers import SignUpSerializer, UserSerializer
from rest_framework.permissions import IsAuthenticated
from django.utils.crypto import get_random_string
from django.core.mail import send_mail



# Create your views here.

@api_view(['POST'])
def register(request):
    data = request.data
    user = SignUpSerializer(data = data)

    print('before')
    if user.is_valid():
        print('valid')

        if not User.objects.filter(username = data['email']).exists():
            print('before create')
            user = User.objects.create(


                first_name  = data['first_name'],

                last_name  = data['last_name'],
                email = data['email'],
                username = data['email'],
                password = make_password(data['password']),
                
            )
            return Response({'details': 'Your Account registered successfully'}, status= status.HTTP_201_CREATED)
        
        else: return Response({'details': 'This email already exist'}, status = status.HTTP_400_BAD_REQUEST)

    else: 
        print('not valid')
        return Response(user.errors)


@api_view(['GET'])
@permission_classes([IsAuthenticated]) # should bo loged in, to do this action
def current_user(request):
    user = UserSerializer(request.user, many = False)
    return Response(user.data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated]) # should bo loged in, to do this action
def update_user(request):
    user = request.user
    data = request.data

    user.first_name = data['first_name']
    user.last_name = data['last_name']
    user.username = data['email']
    user.email = data['email']
    # user.is_staff = data['is_staff']

    if data['password'] != '':
        user.passward = make_password(data['password'])

    user.save()
    serializer = UserSerializer(user, many= False)

    return Response(serializer.data)



def get_current_host(request):
    protocol = request.is_secure() and 'https' or 'http'
    host = request.get_host()
    return "{protocol}://{host}/".format(protocol = protocol, host = host)


@api_view(['POST'])
def forgot_password(request):

    data = request.data
    user = get_object_or_404(User, email = data['email']) 
    token = get_random_string(40)
    expire_date = timezone.now() + timedelta(minutes = 30)

    
    user.profile.reset_password_token = token
    user.profile.reset_password_expire = expire_date
    user.profile.save()
    



    host = get_current_host(request)
    link = "http://localhost:8000/api/reset_password/{token}".format(token = token)
    body = 'Your password reset link is : {link}'.format(link = link)


    send_mail(
        'Password reset from eMarket',
        body,
        'eMarket@gmail.com',
        [data['email']]
    )
    print('here==========')

   
    return Response({'details': 'Password reset sent to {email}'.format(email = data['email'])})




@api_view(['POST'])
def reset_password(request, token):

    data = request.data
    #  “Find the User whose related Profile has reset_password_token == token.”
    user = get_object_or_404(User, profile__reset_password_token = token) 
    if user.profile.reset_password_expire.replace(tzinfo = None) < datetime.now():
        return Response({'error': 'Token is expired'}, status= status.HTTP_400_BAD_REQUEST)
    
    if data['password'] != data['confirmPassword']:
        return Response({'error': 'Passwords are not same'}, status= status.HTTP_400_BAD_REQUEST)

  
    user.password = make_password(data['password'])
    user.profile.reset_password_token = ""
    user.profile.reset_password_expire = None
    user.profile.save()
    user.save()
   
    return Response({'details': 'Password reset done'})
