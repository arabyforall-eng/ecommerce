from django.shortcuts import get_object_or_404, render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .filters import ProductsFilter
from .models import Product, Review
from .serializers import ProductSerializer, ReviewSerializer
from rest_framework.pagination import PageNumberPagination
from django.db.models import Avg




# Create your views here.

@api_view(['GET'])
def get_all_products(request):
    # request is a parameter , but in url while calling this method django passed url with query params (full link) automatically
#   while pagination use query-parameter "page" is default and will not recognize other word untill you define
# "page" is not sized it is the index , page_size is defined below
# "page" should be >= 1

  
    
    #                    request from user(query params)      base source of data
    filterset = ProductsFilter( data=request.GET, queryset= Product.objects.all().order_by('id'))
    # ***** filterset don't have all records but quered records and filtered(using query params) without pagination
    # filterset.qs => filtered data (after applying query params, Invalid or unknown params are ignored; valid ones are applied. )

    print(f"filter first get length is = {filterset.qs.count()}")
    paginator = PageNumberPagination()
    paginator.page_size = 1
    queryset = paginator.paginate_queryset(filterset.qs, request)
    # now is paginated
    serializer = ProductSerializer(queryset, many = True)

    # data which is transported over network
    return Response({'products': serializer.data})


 
@api_view(['GET'])
def get_by_id_product (request, pk ):
    product = get_object_or_404(Product, id = pk)
    serializer = ProductSerializer(product, many = False)
    return Response({'product ': serializer.data})



# may be error happen and still add record to prevent adding if error : use transaction atomic to rollback from database
@api_view(['POST'])
@permission_classes([IsAuthenticated]) # should bo logged in, to do this action
def new_product (request):
    serializer = ProductSerializer(data = request.data)

    if serializer.is_valid():
        product = serializer.save(user = request.user)

        # below wihtout serializing skip validations and typs not optimal
        # product = Product.objects.create(**data, user = request.user) 
        return Response({'product': ProductSerializer(product).data})
    
    else:
        return Response({serializer.errors})
    


# all chararcters must be capital inside api_view 
@api_view(['PUT'])
@permission_classes([IsAuthenticated]) # should bo loged in, to do this action
def update_product (request, pk):
    product = get_object_or_404(Product, id = pk)

    # authorization
    if product.user != request.user:
        return Response({'error': "sorry you can't update this product"}, status= status.HTTP_403_FORBIDDEN, )
    
    product.name = request.data['name']
    product.description = request.data['description']
    product.price = request.data['price']
    product.brand = request.data['brand']
    product.category = request.data['category']
    product.rating = request.data['rating']
    product.stock = request.data['stock']

    product.save()
    serializer = ProductSerializer(product, many = False)

    return Response({'product': serializer.data})
    



@api_view(['DELETE'])
@permission_classes([IsAuthenticated]) # should bo loged in, to do this action
def delete_product (request, pk):
    product = get_object_or_404(Product, id = pk)

    # authorization
    if product.user != request.user:
        return Response({'error': "sorry you can't delete this product"}, status= status.HTTP_403_FORBIDDEN, )
    
   

    product.delete()
    return Response({'details': 'Delete action is done'}, status= status.HTTP_200_OK)
    



@api_view(['POST'])
@permission_classes([IsAuthenticated]) # should bo logged in, to do this action
def create_review (request,pk):
    user = request.user
    data = request.data
    product = get_object_or_404(Product, id = pk)
    review = product.reviews.filter(user = user)
    

    if(data['rating'] <= 0 and data['rating'] > 10):
        return Response({'error': 'Please select between 1 and 5 only'}, status= status.HTTP_400_BAD_REQUEST)
    
    elif review.exists():
        new_review = {'rating': data['rating'], 'comment': data['comment']}
        review.update(**new_review)

        rating = product.reviews.aggregate(avg_ratings = Avg('rating'))
        product.rating = rating['avg_ratings']
        product.save()
        return Response({'details': 'Product review updated'})

    else:
        Review.objects.create(
            user = user,
            product = product,
            rating = data['rating'],
            comment = data['comment'],
        )
        rating = product.reviews.aggregate(avg_ratings = Avg('rating'))
        product.rating = rating['avg_ratings']
        product.save()
        return Response({'details': 'Product review created'})
    



    
@api_view(['DELETE'])
@permission_classes([IsAuthenticated]) # should bo loged in, to do this action
def delete_review (request, pk):
    user = request.user
    product = get_object_or_404(Product, id = pk)
    review = product.reviews.filter(user = user)

    if review.exists():
        review.delete()
        rating = product.reviews.aggregate(avg_ratings = Avg('rating'))
        if rating['avg_ratings'] is None:
            rating['avg_ratings'] = 0
            product.rating = rating['avg_ratings']
            product.save()
            return Response({'details': 'Product review deleted'})

    else: 
        return Response({'error': 'Review not found'}, status= status.HTTP_404_NOT_FOUND)



    # authorization
    if product.user != request.user:
        return Response({'error': "sorry you can't delete this product"}, status= status.HTTP_403_FORBIDDEN, )
    
   

    product.delete()
    return Response({'details': 'Delete action is done'}, status= status.HTTP_200_OK)
    




    

