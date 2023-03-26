import json
import os
from rest_framework import permissions
from rest_framework.viewsets import ViewSet
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db.models import F, Value, Func

from product.serializers import ProductSerializer, ProductImageSerializer, ProductVariantSerializer,\
    ProductVariantPriceSerializer
from product.models import Product, Variant, ProductVariant, ProductVariantPrice, ProductImage


class ProductCreateViewSet(ViewSet):
    def create(self, request):
        try:
            print('request data = ', request.data)

            # product data saved
            product_details = json.loads(request.data['product_details'])

            if product_details['title'] == '':
                dict_response = {
                    "error": True,
                    'message': "product title required"
                }
                return Response(dict_response, status=status.HTTP_400_BAD_REQUEST)
            if product_details['sku'] == '':
                dict_response = {
                    "error": True,
                    'message': "product sku required"
                }
                return Response(dict_response, status=status.HTTP_400_BAD_REQUEST)
            if product_details['sku'] != "":
                product_sku = Product.objects.filter(sku=product_details['sku'])
                if len(product_sku) != 0:
                    dict_response = {
                        "error": True,
                        'message': "product sku already exits"
                    }
                    return Response(dict_response, status=status.HTTP_400_BAD_REQUEST)
            if product_details['description'] == '':
                dict_response = {
                    "error": True,
                    'message': "product description required"
                }
                return Response(dict_response, status=status.HTTP_400_BAD_REQUEST)
            product_create = {}
            product_create['title'] = product_details['title']
            product_create['sku'] = product_details['sku']
            product_create['description'] = product_details['description']
            product_create_serializer = ProductSerializer(data=product_create, context={'request': request})
            product_create_serializer.is_valid(raise_exception=True)
            product_create_serializer.save()

            product_id = product_create_serializer.data['id']
            print("product id = ", product_id)
            print("**"*30)
            print("**"*30)

            # Save Product Image
            product_image = request.FILES.get("product_image")
            print("product_image = ", product_image)
            if product_image:
                server_file_location = os.path.join(settings.MEDIA_ROOT)  # Where save the file
                fs = FileSystemStorage(location=server_file_location)
                filename = fs.save(f"{product_image.name}", product_image)

                final_file_path = settings.HOST + settings.MEDIA_URL + filename  # file path
                print("final_file_path = ", final_file_path)
                product_image_create = {}
                product_image_create['product'] = Product.objects.get(id=product_id).id
                product_image_create['file_path'] = final_file_path
                product_image_serializer = ProductImageSerializer(data=product_image_create,
                                                                  context={'request': request})
                product_image_serializer.is_valid(raise_exception=True)
                product_image_serializer.save()

            # Save Product Variants
            product_variants = json.loads(request.data["product_variants"])
            print("product_variants = ", product_variants)
            for product_variant in product_variants:
                option = product_variant.get("option")
                print("option = ", option)
                option = Variant.objects.get(id=option)
                print("option = ", option)
                if option:
                    # Create product variant
                    tags = product_variant.get("tags")
                    print("tags = ", tags)
                    for tag in tags:
                        product_variant = {}
                        product_variant['variant_title'] = tag
                        product_variant['variant'] = option.id
                        product_variant['product'] = Product.objects.get(id=product_id).id
                        product_variant_serializer = ProductVariantSerializer(data=product_variant,
                                                                              context={'request': request})
                        product_variant_serializer.is_valid(raise_exception=True)
                        product_variant_serializer.save()
                        print("product variant id = ", product_variant_serializer.data['id'])
                print("=="*20)
            # Save Data Product Variant Prices
            product_variant_prices = json.loads(request.data['product_variant_prices'])
            print("product_variant_prices = ", product_variant_prices)
            for product_variant_price in product_variant_prices:
                    variants = product_variant_price.get("title").split("/")
                    variants = variants[:len(variants) - 1]
                    price = product_variant_price.get("price")
                    stock = product_variant_price.get("stock")
                    print("variants = ", variants)

                    print("price = ", price)
                    print("stock = ", stock)
                    product_variant_one = 0
                    product_variant_two = 0
                    product_variant_three = 0

                    if len(variants) == 1:
                        print(1)
                        product_variant_one = ProductVariant.objects.filter(variant_title=variants[0]).first()
                    if len(variants) == 2:
                        print(2)
                        product_variant_one = ProductVariant.objects.filter(variant_title=variants[0]).first()
                        product_variant_two = ProductVariant.objects.filter(variant_title=variants[1]).first()
                    if len(variants) == 3:
                        print(3)
                        product_variant_one = ProductVariant.objects.filter(variant_title=variants[0]).first()
                        product_variant_two = ProductVariant.objects.filter(variant_title=variants[1]).first()
                        product_variant_three = ProductVariant.objects.filter(variant_title=variants[2]).first()
                    if product_variant_one != 0:
                        product_variant_one = product_variant_one.id
                    else:
                        product_variant_one = ''
                    if product_variant_two != 0:
                        product_variant_two = product_variant_two.id
                    else:
                        product_variant_two = ''
                    if product_variant_three != 0:
                        product_variant_three = product_variant_three.id
                    else:
                        product_variant_three = ''
                    print(" ==product_variant_one ", product_variant_one)
                    print(" ==product_variant_two ", product_variant_two)
                    print(" ==product_variant_three ", product_variant_three)
                    product_variant_price_create = {}
                    product_variant_price_create['product_variant_one'] = product_variant_one
                    product_variant_price_create['product_variant_two'] = product_variant_two
                    product_variant_price_create['product_variant_three'] = product_variant_three
                    product_variant_price_create['price'] = price
                    product_variant_price_create['stock'] = stock
                    product_variant_price_create['product'] = Product.objects.get(id=product_id).id
                    product_variant_price_create_serializer = ProductVariantPriceSerializer(
                        data=product_variant_price_create,
                        context={"request": request}
                    )
                    product_variant_price_create_serializer.is_valid(raise_exception=True)
                    product_variant_price_create_serializer.save()

            return Response({"success": "Product is created successfully"})
        except Exception as e:
            Product.objects.get(id=product_id).delete()
            print('e = ', e)
            dict_response = {
                'error': True,
                'message': str(e)
            }
            return Response(dict_response, status=status.HTTP_400_BAD_REQUEST)
