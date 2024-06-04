from .models import ContactMessage
from .models import Camera_History
from .models import Person
from .models import Admin
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from django.http import QueryDict
from django.http import JsonResponse
from .models import Location, Camera, Person, Community, UsersInCommunity, Camera_History, SecurityPersonnel, Admin, AdminLoginHistory
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from .models import Camera_History, Person, Camera
import json
from django.utils.dateparse import parse_date
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.hashers import check_password
from django.core.files.base import ContentFile
from datetime import datetime


def location_list(request):
    locations = Location.objects.all()
    data = [{'name': location.name} for location in locations]
    return JsonResponse(data, safe=False)


def camera_list(request):
    cameras = Camera.objects.all()
    data = [{'name': camera.name, 'location': camera.location.name}
            for camera in cameras]
    return JsonResponse(data, safe=False)


def person_list(request):
    persons = Person.objects.all()
    data = [{'id': person.pk,  'first_name': person.first_name, 'last_name': person.last_name,
            'birth_date': person.birth_date, 'created_at': person.created_at,
             'photo_url': person.photo.url if person.photo else None} for person in persons]
    return JsonResponse(data, safe=False)


@csrf_exempt
def delete_person(request, pk):
    if request.method == 'DELETE':
        try:
            person = Person.objects.get(pk=pk)
            person.delete()
            return JsonResponse({'message': 'Person deleted successfully'})
        except Person.DoesNotExist:
            return JsonResponse({'error': 'Person not found'}, status=404)
    else:
        # Method not allowed
        return HttpResponseNotAllowed(['DELETE'])


# def person_detail(request, pk):
#     try:
#         person = Person.objects.get(pk=pk)
#         users_in_community = UsersInCommunity.objects.filter(
#             person_id=pk).first()
#         community_id = users_in_community.Community_ID.Community_ID if users_in_community else None

#         data = {
#             'id': person.pk,
#             'first_name': person.first_name,
#             'last_name': person.last_name,
#             'birth_date': person.birth_date,
#             'created_at': person.created_at,
#             'email': person.email,
#             'photo_url': person.photo.url if person.photo else None,
#             'Community_ID': community_id  # Retrieved community ID based on person ID
#         }
#         return JsonResponse(data)
#     except Person.DoesNotExist:
#         return JsonResponse({'error': 'Person not found'}, status=404)
def person_detail(request, pk):
    try:
        person = Person.objects.get(pk=pk)
        users_in_community = UsersInCommunity.objects.filter(
            person_id=pk)
        community_ids = [
            u.Community_ID.Community_ID for u in users_in_community]

        data = {
            'id': person.pk,
            'first_name': person.first_name,
            'last_name': person.last_name,
            'birth_date': person.birth_date,
            'created_at': person.created_at,
            'email': person.email,
            'photo_url': person.photo.url if person.photo else None,
            'Community_IDs': community_ids  # List of community IDs associated with the person
        }
        return JsonResponse(data)
    except Person.DoesNotExist:
        return JsonResponse({'error': 'Person not found'}, status=404)


def person_image_view(request, pk):
    person = get_object_or_404(Person, pk=pk)
    if person.photo:
        with open(person.photo.path, 'rb') as f:
            image_data = f.read()
        # Adjust content type based on your image format
        return HttpResponse(image_data, content_type="image/jpeg")
    else:
        return HttpResponse(status=404)

# def community_list(request):
#     communities = Community.objects.all()
#     data = [{'name': community.name, 'Community_ID': community.Community_ID}
#             for community in communities]
#     return JsonResponse(data, safe=False)


def community_list(request):
    communities = Community.objects.all()
    data = [{'Community_ID': community.Community_ID}
            for community in communities]
    return JsonResponse(data, safe=False)


@csrf_exempt
def delete_community_admin(request):
    if request.method == 'DELETE':
        try:
            data = json.loads(request.body)
            community_id = data.get('community_id')
            if community_id is None:
                return JsonResponse({'error': 'Community ID is required'}, status=400)

            # Get the community by its ID
            community = Community.objects.get(Community_ID=community_id)

            # Delete the community
            community.delete()

            return JsonResponse({'message': 'Community deleted successfully'})
        except Community.DoesNotExist:
            return JsonResponse({'error': 'Community not found'}, status=404)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def create_community(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        # Assuming no data is needed to create a community
        community = Community.objects.create()
        person_id = data.get('person_id')
        join_date = timezone.now().date()  # Set join_date to current date
        person = Person.objects.get(pk=person_id)
        print(community)
        user_in_community = UsersInCommunity(
            person=person, Community_ID=community, join_date=join_date)
        user_in_community.save()
        return JsonResponse({'message': 'Community created successfully', 'Community_ID': community.Community_ID})
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def check_community_id(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        community_id = data.get('community_id', None)
        if community_id is not None:
            try:
                community = Community.objects.get(Community_ID=community_id)
                return JsonResponse({'message': 'Community exists', 'Community_ID': community.Community_ID})
            except Community.DoesNotExist:
                return JsonResponse({'error': 'Community does not exist'}, status=404)
        else:
            return JsonResponse({'error': 'Invalid data provided'}, status=400)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def delete_community(request, community_id):
    if request.method == 'POST':
        try:
            # Extract person_id from the request data

            data = json.loads(request.body)
            person_id = data.get('person_id')

            # Filter UsersInCommunity object based on both community_id and person_id
            user_in_community = UsersInCommunity.objects.get(
                Community_ID=community_id, person_id=person_id)
            # Delete the filtered instance
            user_in_community.delete()

            return JsonResponse({'message': 'User removed from community successfully'}, status=200)
        except UsersInCommunity.DoesNotExist:
            return JsonResponse({'error': 'No such user in community'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


def users_in_community_list(request):
    users_in_community = UsersInCommunity.objects.all()
    data = [{'person': user.person.first_name, 'Community_ID': user.Community_ID.Community_ID,
             'join_date': user.join_date} for user in users_in_community]
    return JsonResponse(data, safe=False)


def user_communities_No(request, user_id):
    try:
        user_communities = UsersInCommunity.objects.filter(person_id=user_id)
        data = [{
            'Community_ID': user_in_community.Community_ID.Community_ID,
            'Join_Date': user_in_community.join_date
        } for user_in_community in user_communities]
        return JsonResponse(data, safe=False)
    except UsersInCommunity.DoesNotExist:
        return JsonResponse({'error': 'User not found or not associated with any communities'}, status=404)


def users_in_community_by_id(request, community_id):
    # Query the database to retrieve users in the specified community
    users_in_community = UsersInCommunity.objects.filter(
        Community_ID=community_id)

    # Serialize the user data into JSON format
    data = [{'user_first': user.person.first_name,
             'photo_url': user.person.photo.url if user.person.photo else None,
             'Community_ID': user.Community_ID.Community_ID,
             'join_date': user.join_date,
             'user_last': user.person.last_name,
             'user_id': user.person.pk}
            for user in users_in_community]

    # Return the JSON response with the user data
    return JsonResponse(data, safe=False)


@csrf_exempt
def add_user_to_community(request):
    if request.method == 'POST':
        # Decode JSON data from request body
        data = json.loads(request.body)

        # Extract data for creating a new UsersInCommunity object
        person_id = data.get('person_id')
        community_id = data.get('community_id')
        join_date = data.get('join_date')

        try:
            # Get person and community objects
            person = Person.objects.get(pk=person_id)
            community = Community.objects.get(pk=community_id)

            if UsersInCommunity.objects.filter(person=person, Community_ID=community).exists():
                return JsonResponse({'error': 'User already exists in the community'}, status=400)
            else:
                # Create a new UsersInCommunity object
                user_in_community = UsersInCommunity(
                    person=person, Community_ID=community, join_date=join_date)
                user_in_community.save()
                # Return a success response
                return JsonResponse({'message': 'User added to community successfully'})
        except (Person.DoesNotExist, Community.DoesNotExist) as e:
            # Return an error response if person or community does not exist
            return JsonResponse({'error': 'Person or Community not found'}, status=404)
    else:
        # Return an error response for unsupported methods
        return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def edit_person_detail(request, pk):
    if request.method == 'PUT':
        try:
            # Get the person object
            person = Person.objects.get(pk=pk)

            # Decode JSON data from request body
            data = json.loads(request.body)

            # Update person details if provided in the request
            if 'first_name' in data:
                person.first_name = data['first_name']
            if 'last_name' in data:
                person.last_name = data['last_name']
            if 'birth_date' in data:
                person.birth_date = data['birth_date']
            if 'email' in data:
                person.email = data['email']
            if 'photo' in data:
                # Assuming you handle photo upload separately
                # Update photo URL if provided
                person.photo = data['photo']

            # Save the updated person object
            person.save()

            # Return the updated person details
            updated_data = {
                'id': person.pk,
                'first_name': person.first_name,
                'last_name': person.last_name,
                'birth_date': person.birth_date,
                'created_at': person.created_at,
                'email': person.email,
                'photo': person.photo.url if person.photo else None
            }
            return JsonResponse(updated_data)
        except Person.DoesNotExist:
            return JsonResponse({'error': 'Person not found'}, status=404)
    else:
        # Return an error response for unsupported methods
        return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def remove_user_from_community(request):
    if request.method == 'POST':
        # Decode JSON data from request body
        data = json.loads(request.body)

        # Extract data for removing a user from the community
        person_id = data.get('person_id')
        community_id = data.get('community_id')

        try:
            # Get person and community objects
            person = Person.objects.get(pk=person_id)
            community = Community.objects.get(pk=community_id)

            # Check if the user exists in the community
            try:
                user_in_community = UsersInCommunity.objects.get(
                    person=person, Community_ID=community)
            except ObjectDoesNotExist:
                return JsonResponse({'error': 'User does not exist in the community'}, status=400)

            # Remove the user from the community
            user_in_community.delete()

            # Return a success response
            return JsonResponse({'message': 'User removed from community successfully'})
        except (Person.DoesNotExist, Community.DoesNotExist) as e:
            # Return an error response if person or community does not exist
            return JsonResponse({'error': 'Person or Community not found'}, status=404)
    else:
        # Return an error response for unsupported methods
        return JsonResponse({'error': 'Method not allowed'}, status=405)


def camera_history_list(request):
    camera_history = Camera_History.objects.all()
    data = [{'person': history.person.first_name, "person_id": history.person.pk, 'camera': history.camera.name,
             'checkIn_time': history.checkIn_time, 'checkOut_time': history.checkOut_time} for history in camera_history]
    return JsonResponse(data, safe=False)


# class CameraHistoryConsumer(WebsocketConsumer):
#     def connect(self):
#         self.accept()

#     def disconnect(self, close_code):
#         pass

#     def fetch_camera_history(self, event):
#         camera_history = Camera_History.objects.all()
#         data = [{'person': history.person.first_name, 'camera': history.camera.name,
#                  'checkIn_time': history.checkIn_time, 'checkOut_time': history.checkOut_time} for history in camera_history]
#         self.send(text_data=json.dumps(data))


def camera_history_for_person(request, person_id):
    try:
        camera_history = Camera_History.objects.filter(person__id=person_id)
        data = [{'person': history.person.first_name,
                 'person_id': history.id,
                 'camera': history.camera.name,
                 'checkIn_time': history.checkIn_time,
                 'checkOut_time': history.checkOut_time} for history in camera_history]
        return JsonResponse(data, safe=False)
    except Camera_History.DoesNotExist:
        return JsonResponse({'error': 'Camera history not found for the specified person'}, status=404)


def security_personnel_list(request):
    security_personnels = SecurityPersonnel.objects.all()
    data = [{'first_name': personnel.first_name, 'last_name': personnel.last_name,
             'birth_date': personnel.birth_date, 'created_at': personnel.created_at} for personnel in security_personnels]
    return JsonResponse(data, safe=False)


def admin_list(request):
    admins = Admin.objects.all()
    data = [{'first_name': admin.first_name, 'last_name': admin.last_name,
             'created_at': admin.created_at, 'birth_date': admin.birth_date} for admin in admins]
    return JsonResponse(data, safe=False)


def admin_details(request, admin_id):
    admin = get_object_or_404(Admin, id=admin_id)
    data = {
        'id': admin.id,
        'first_name': admin.first_name,
        'last_name': admin.last_name,
        'created_at': admin.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'birth_date': admin.birth_date.strftime('%Y-%m-%d'),
        'username': admin.username,
        'image_url': admin.image.url if admin.image else None
    }
    return JsonResponse(data)


@csrf_exempt
def edit_admin_detail(request, pk):
    if request.method == 'PUT':
        try:
            # Get the admin object
            admin = Admin.objects.get(pk=pk)

            # Decode JSON data from request body
            data = json.loads(request.body)

            # Update admin details if provided in the request
            if 'first_name' in data:
                admin.first_name = data['first_name']
            if 'last_name' in data:
                admin.last_name = data['last_name']
            if 'birth_date' in data:
                admin.birth_date = data['birth_date']
            if 'username' in data:
                admin.username = data['username']
            if 'password' in data:
                admin.password = data['password']
            if 'image' in data:
                # Assuming you handle image upload separately
                # Update image URL if provided
                admin.image = data['image']

            # Save the updated admin object
            admin.save()

            # Return the updated admin details
            updated_data = {
                'id': admin.pk,
                'first_name': admin.first_name,
                'last_name': admin.last_name,
                'birth_date': admin.birth_date,
                'created_at': admin.created_at,
                'username': admin.username,
                'image': admin.image.url if admin.image else None
            }
            return JsonResponse(updated_data)
        except Admin.DoesNotExist:
            return JsonResponse({'error': 'Admin not found'}, status=404)
    else:
        # Return an error response for unsupported methods
        return JsonResponse({'error': 'Method not allowed'}, status=405)


def admin_image_view(request, admin_id):
    admin = get_object_or_404(Admin, pk=admin_id)
    if admin.image:
        image_data = open(admin.image.path, "rb").read()
        # Adjust content type based on your image format
        return HttpResponse(image_data, content_type="image/jpeg")
    else:
        return HttpResponse(status=404)  # Return 404 if the admin has no image


@csrf_exempt  # Note: Be cautious with CSRF exemption in production
def add_camera_history(request):
    if request.method == 'POST':
        # Parse the JSON body of the request
        try:
            data = json.loads(request.body)
            person_name = data.get('name')
            person_id = data.get('id')
            checkIn_time = data.get('checkIn_time')
            checkOut_time = data.get('checkOut_time')
            camera_id = data.get('camera_id')
            print(data)
            print(checkIn_time)
            Cid = camera_id+3

            # Validate and fetch related instances
            person = Person.objects.filter(
                id=person_id).first()
            camera = Camera.objects.filter(id=Cid).first()

            if not person or not camera:
                return HttpResponseBadRequest("Invalid person ID/name or camera ID provided.")

            # Create the Camera_History record
            camera_history = Camera_History(
                person=person, camera=camera, checkIn_time=checkIn_time, checkOut_time=checkOut_time)
            camera_history.save()

            # Return success response
            return JsonResponse({'success': True, 'message': 'Camera history record added successfully.'})
        except Exception as e:
            return HttpResponseBadRequest(f"Error processing request: {str(e)}")
    else:
        # If not a POST request, return a 405 Method Not Allowed response
        return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)


@csrf_exempt
def add_security_personnel(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            first_name = data['first_name']
            last_name = data['last_name']
            birth_date = parse_date(data['birth_date'])

            security_personnel = SecurityPersonnel(
                first_name=first_name,
                last_name=last_name,
                birth_date=birth_date
            )
            security_personnel.save()

            return JsonResponse({'success': True, 'message': 'Security personnel added successfully.'})
        except Exception as e:
            return HttpResponseBadRequest(f"Error processing request: {str(e)}")
    else:
        return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)


@csrf_exempt
def add_admin(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            first_name = data['first_name']
            last_name = data['last_name']
            username = data['username']
            password = data['password']
            birth_date = parse_date(data['birth_date'])
            created_at = parse_date(data['created_at'])

            admin = Admin(
                first_name=first_name,
                last_name=last_name,
                birth_date=birth_date,
                created_at=created_at,
                username=username

            )
            admin.set_password(password)  # Set the hashed password
            admin.save()

            return JsonResponse({'success': True, 'message': 'Admin added successfully.'})
        except Exception as e:
            return HttpResponseBadRequest(f"Error processing request: {str(e)}")
    else:
        return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)


@csrf_exempt
def add_person(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        birth_date = request.POST.get('birth_date')
        email = request.POST.get('email')
        photo = request.FILES.get('photo')
        username = request.POST.get('username')
        password = request.POST.get('password')
        # Convert birth_date from string to date object
        birth_date_obj = birth_date
        if Person.objects.filter(username=username).exists() or Person.objects.filter(email=email).exists():
            return JsonResponse({'error': 'Username or email already exists'}, status=400)
        # Assuming validation for each field is done here
        person = Person(
            first_name=first_name,
            last_name=last_name,
            birth_date=birth_date_obj,
            email=email,
            photo=photo,
            username=username,
            password=password,
        )
        if password:
            person.password = make_password(password)

        # The save method in your Person model already handles the logic for the photo
        person.save()
        return JsonResponse({'status': 'success', 'person_id': person.id})

    return JsonResponse({'error': 'This method is not allowed'}, status=405)


# def login_person(request):
#     if request.method == 'POST':
#         # Decode JSON data from request body
#         data = json.loads(request.body)

#         # Extract username and password
#         username = data.get('username')
#         password = data.get('password')

#         try:
#             # Retrieve the person based on the username
#             person = Person.objects.get(username=username)
#         except Person.DoesNotExist:
#             return JsonResponse({'error': 'Invalid username or password'}, status=400)

#         # Check if the provided password matches the hashed password in the database
#         # if check_password(password, person.password):
#         #     # Manually create session to log in person
#         #     return JsonResponse({'message': 'Login successful'})
#         if check_password(password, person.password):
#             # Generate JWT token
#             refresh = RefreshToken.for_user(person)
#             request.session['person_id'] = person.id
#             token = {
#                 'refresh': str(refresh),
#                 'access': str(refresh.access_token),
#             }
#             return JsonResponse({'message': 'Login successful', 'token': token})
#         else:
#             return JsonResponse({'error': 'Invalid username or password'}, status=400)
#     else:
#         # Return an error response for unsupported methods
#         return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def login_person(request):
    if request.method == 'POST':
        # Decode JSON data from request body
        data = json.loads(request.body)

        # Extract username and password
        username = data.get('username')
        password = data.get('password')

        try:
            # Retrieve the person based on the username
            person = Person.objects.get(username=username)
        except Person.DoesNotExist:
            return JsonResponse({'error': 'Invalid username or password'}, status=400)

        # Check if the provided password matches the hashed password in the database
        if check_password(password, person.password):
            # Generate JWT token
            refresh = RefreshToken.for_user(person)
            token = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
            data = {
                "user_id": person.pk,
            }
            # Set the token in an HTTP cookie
            response = JsonResponse(
                {'message': 'Login successful', "data": data})
            response.set_cookie('auth_token', token['access'], httponly=True)
            return response
        else:
            return JsonResponse({'error': 'Invalid username or password'}, status=400)
    else:
        # Return an error response for unsupported methods
        return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def login_admin(request):
    # if request.method == 'POST':
    #     # username = request.POST.get('username')
    #     # password = request.POST.get('password')
    #     data = json.loads(request.body)

    #     # Extract username and password
    #     username = data.get('username')
    #     password = data.get('password')
    #     try:
    #         admin = Admin.objects.get(username=username)
    #         if admin.check_password(password):
    #             # Authentication successful
    #             # Perform login logic here
    #             return JsonResponse({'message': 'Login successful'})
    #         else:
    #             return JsonResponse({'error': 'Invalid username or password'}, status=400)
    #     except Admin.DoesNotExist:
    #         return JsonResponse({'error': 'Admin not found'}, status=404)
    # else:
    #     return JsonResponse({'error': 'Method not allowed'}, status=405)
    if request.method == 'POST':
        # Decode JSON data from request body
        data = json.loads(request.body)

        # Extract username and password
        username = data.get('username')
        password = data.get('password')

        try:
            # Retrieve the person based on the username
            admin = Admin.objects.get(username=username)
        except Admin.DoesNotExist:
            return JsonResponse({'error': 'Invalid username'}, status=400)

        # Check if the provided password matches the hashed password in the database
        if check_password(password, admin.password):
            # Manually create session to log in person
            request.session['admin_id'] = admin.id
            login_history = AdminLoginHistory(
                admin=admin, login_time=datetime.now())
            login_history.save()
            data = {
                "admin_name": admin.first_name,
                "Admin_id": admin.id,
            }
            return JsonResponse({'message': 'Login successful', "data": data})
        else:
            return JsonResponse({'error': 'Invalid username or password'}, status=400)
    else:
        # Return an error response for unsupported methods
        return JsonResponse({'error': 'Method not allowed'}, status=405)


def get_counts(request):
    person_count = Person.objects.count()
    community_count = Community.objects.count()

    data = {
        'person_count': person_count,
        'community_count': community_count
    }

    return JsonResponse(data)


@csrf_exempt
def admin_login_history(request, admin_id):
    if request.method == 'GET':
        try:
            # Get the admin login history
            history = AdminLoginHistory.objects.filter(
                admin=admin_id).order_by('-login_time')
            # Serialize the data
            history_data = [{'login_time': login.login_time}
                            for login in history]

            # Return the JSON response
            return JsonResponse({'history': history_data})
        except:
            return JsonResponse({'error': "error"})
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

# views.py


@csrf_exempt  # CSRF exemption to allow cross-origin POST requests
def contact_view(request):
    if request.method == 'POST':
        # Parse JSON data from request body
        try:
            form_data = json.loads(request.body)
            first_name = form_data.get('fname')
            last_name = form_data.get('lname')
            phoneno = form_data.get('phoneno')
            email = form_data.get('email')
            message = form_data.get('message')
            selected_subject = form_data.get('selectedSubject')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

        # Create a ContactMessage instance
        message = ContactMessage(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phoneno=phoneno,
            message=message,
            subject=selected_subject
        )

        # Save the message instance
        message.save()

        # Return success response
        return JsonResponse({'status': 'success', 'message_id': message.id})

    # Return error response for disallowed method
    return JsonResponse({'error': 'This method is not allowed'}, status=405)
