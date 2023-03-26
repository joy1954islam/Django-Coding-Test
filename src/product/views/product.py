from django.views import generic
from django.views.generic import ListView, CreateView, UpdateView
from product.models import Variant, Product, ProductVariantPrice, ProductVariant, ProductImage
from django.db.models import Q


class CreateProductView(generic.TemplateView):
    template_name = 'products/create.html'

    def get_context_data(self, **kwargs):
        context = super(CreateProductView, self).get_context_data(**kwargs)
        variants = Variant.objects.filter(active=True).values('id', 'title')
        context['product'] = True
        context['variants'] = list(variants.all())
        return context


class ListProductView(ListView):
    template_name = 'products/list.html'
    model = Product
    paginate_by = 2
    context_object_name = 'product_list'

    def get_queryset(self):
        product_queryset = Product.objects.all().order_by("-id")
        # Filtering data
        product_title = self.request.GET.get('title')
        date = self.request.GET.get('date')
        variant = self.request.GET.get('variant')
        price_from = self.request.GET.get('price_from')
        price_to = self.request.GET.get('price_to')
        if product_title:
            product_queryset = product_queryset.filter(
                title__icontains=product_title
            )
        if variant:
            product_queryset = product_queryset.filter(
                productvariant__variant_title=variant
            ).distinct()
        if date:
            product_queryset = product_queryset.filter(
                created_at__date=date
            )
        if price_from and price_to:
            product_queryset = product_queryset.filter(
                Q(productvariantprice__price__gte=price_from) &
                Q(productvariantprice__price__lte=price_to)
            ).distinct()
        elif price_from and not price_to:
            product_queryset = product_queryset.filter(productvariantprice__price__gte=price_from).distinct()
        elif not price_from and price_to:
            product_queryset = product_queryset.filter(productvariantprice__price__lte=price_to).distinct()

        return product_queryset

    def get_context_data(self, **kwargs):
        context = super(ListProductView, self).get_context_data(**kwargs)
        context['product'] = True
        # Variants
        variants = Variant.objects.all()
        variant_dict = {}
        for variant in variants:
            variant_dict[variant.title] = list(
                ProductVariant.objects.filter(variant=variant).values_list("variant_title", flat=True).distinct())
        context['variant_list'] = variant_dict

        # filter data
        if self.request.GET:
            product_title = self.request.GET.get('title')
            date = self.request.GET.get('date')
            variant = self.request.GET.get('variant')
            price_from = self.request.GET.get('price_from')
            price_to = self.request.GET.get('price_to')
            context['filter_product_title'] = product_title
            context['filter_date'] = date
            context['filter_product_variant'] = variant
            context['filter_price_from'] = price_from
            context['filter_price_to'] = price_to
        context['filter_product_title'] = ''
        context['filter_date'] = ''
        context['product_variant'] = ''
        context['filter_price_from'] = ''
        context['filter_price_to'] = ''
        return context


class UpdateProductView(generic.TemplateView):
    template_name = 'products/update.html'

    def get_context_data(self, **kwargs):
        context = super(UpdateProductView, self).get_context_data(**kwargs)
        variants = Variant.objects.filter(active=True).values('id', 'title')
        context['product'] = True
        context['variants'] = list(variants.all())
        context['product_id'] = kwargs.get('product_id')
        return context
