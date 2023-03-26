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

from product.serializers import ProductSerializer, ProductImageSerializer, ProductVariantSerializer, \
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
            print("**" * 30)
            print("**" * 30)

            # Save Product Image
            product_image = request.FILES.get("product_image")
            print("product_image = ", product_image)
            if product_image:
                fs = FileSystemStorage()
                file = fs.save(product_image.name, product_image)
                print("file = ", file)
                final_file_path = settings.HOST + fs.url(file)
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
                print("==" * 20)
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
            dict_response = {
                "error": False,
                'message': "Product is created successfully"
            }
            return Response(dict_response, status=status.HTTP_200_OK)
        except Exception as e:
            Product.objects.get(id=product_id).delete()
            print('e = ', e)
            dict_response = {
                'error': True,
                'message': str(e)
            }
            return Response(dict_response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        product_queryset = Product.objects.filter(id=pk).first()
        if not product_queryset:
            dict_response = {
                "error": True,
                'message': "product not found"
            }
            return Response(dict_response, status=status.HTTP_400_BAD_REQUEST)
        data = {}
        product_details_data = ProductSerializer(product_queryset).data
        data['product_details'] = product_details_data

        # product variant price data format change
        product_variant_price_data = []
        product_variant_prices = product_queryset.productvariantprice_set.all()
        for product_variant_price in product_variant_prices:
            title = ""
            if product_variant_price.product_variant_one:
                title = f"{product_variant_price.product_variant_one.variant_title}/"
            if product_variant_price.product_variant_two:
                title = title + f"{product_variant_price.product_variant_two.variant_title}/"
            if product_variant_price.product_variant_three:
                title = title + f"{product_variant_price.product_variant_three.variant_title}/"

            product_variant_price_modify_data = {
                "title": title,
                "price": product_variant_price.price,
                "stock": product_variant_price.stock
            }
            product_variant_price_data.append(product_variant_price_modify_data)

        data['product_variant_prices'] = product_variant_price_data

        # product variants data format for update page
        variants = product_queryset.productvariant_set.values_list("variant__id", flat=True).distinct()
        product_variants = []
        for variant in variants:
            tags = product_queryset.productvariant_set.filter(variant__id=variant).values_list("variant_title",
                                                                                               flat=True)
            product_variants.append({"option": variant, "tags": tags})
        data['product_variants'] = product_variants
        product_image_queryset = ProductImage.objects.filter(product__id=pk)
        data['product_image'] = ProductImageSerializer(product_image_queryset, many=True).data

        dict_response = {
            'error': False,
            'message': "product retrieve",
            'data': data
        }
        return Response(data, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        print("request data = ", request.data)
        try:
            product_queryset = Product.objects.filter(id=pk)
            if len(product_queryset) == 0:
                dict_response = {
                    "error": True,
                    'message': "product not found"
                }
                return Response(dict_response, status=status.HTTP_400_BAD_REQUEST)
            else:
                product_queryset = product_queryset[0]
                product_id = product_queryset.id
                print("product id = ", product_id)
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
            product_create_serializer = ProductSerializer(product_queryset, data=product_create, partial=True,
                                                          context={'request': request})
            product_create_serializer.is_valid(raise_exception=True)
            product_create_serializer.save()

            # update Product Image
            product_image = request.FILES.get("product_image")
            print("product_image = ", product_image)
            if product_image:
                fs = FileSystemStorage()
                file = fs.save(product_image.name, product_image)
                print("file = ", file)
                final_file_path = settings.HOST + fs.url(file)
                print("final_file_path = ", final_file_path)

                product_image_queryset = ProductImage.objects.filter(product__id=product_id)
                print("product_image_queryset = ", product_image_queryset)
                if len(product_image_queryset) != 0:
                    product_image_create = {}
                    product_image_create['file_path'] = final_file_path
                    product_image_serializer = ProductImageSerializer(product_image_queryset[0],
                                                                      data=product_image_create,
                                                                      partial=True,
                                                                      context={'request': request})
                    product_image_serializer.is_valid(raise_exception=True)
                    product_image_serializer.save()
                else:
                    product_image_create = {}
                    product_image_create['product'] = Product.objects.get(id=product_id).id
                    product_image_create['file_path'] = final_file_path
                    product_image_serializer = ProductImageSerializer(data=product_image_create,
                                                                      context={'request': request})
                    product_image_serializer.is_valid(raise_exception=True)
                    product_image_serializer.save()

            # Update Product Variants

            product_variants = json.loads(request.data["product_variants"])
            print("product_variants = ", product_variants)
            ProductVariant.objects.filter(product__id=product_id).delete()  # delete old product variant
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
                print("==" * 20)

            # Save Data Product Variant Prices
            product_variant_prices = json.loads(request.data['product_variant_prices'])
            ProductVariantPrice.objects.filter(product__id=product_id).delete()  # Delete all old data
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

            dict_response = {
                "error": False,
                'message': "Product is update successfully"
            }
            return Response(dict_response, status=status.HTTP_200_OK)
        except Exception as e:
            print('e = ', e)
            dict_response = {
                'error': True,
                'message': str(e)
            }
            return Response(dict_response, status=status.HTTP_400_BAD_REQUEST)
