from django.db import models
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# from wagtail.contrib.routable_page.models import register

# Create your models here.
from modelcluster.fields import ParentalKey
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.core.models import Page, Orderable
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index


class HomePage(Page):
    intro = models.CharField(max_length=250, blank=True, null=True)
    date = models.DateField("Post date", blank=True, null=True)
    read_time = RichTextField(blank=True, null=True)
    image = models.ForeignKey(
        'wagtailimages.Image', on_delete=models.SET_NULL, blank=True, null=True, related_name='+'
    )
    body = RichTextField(blank=True, null=True)
    int_section_title = RichTextField(blank=True, null=True)
    int_section_body = RichTextField(blank=True, null=True)


    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        FieldPanel('read_time'),
        FieldPanel('body'),
        FieldPanel('int_section_title'),
        FieldPanel('int_section_body'),
        FieldPanel('date'),
        ImageChooserPanel('image'),
    ]

    def get_context(self, request):
        # Update context to include only published posts, ordered by reverse-chron
        context = super().get_context(request)
        blogpages = self.get_children().live().order_by('-first_published_at')
        context['blogpages'] = blogpages
        return context

    def blogs(self):
        blogs = BlogPage.objects.all() 
        blogs = blogs.order_by('-date')[:3]
        return blogs
        
    class Meta:
        verbose_name = "Index Page"




class BlogPage(RoutablePageMixin,Page):
    intro = models.CharField(max_length=250, blank=True, null=True)
    date = models.DateField("Post date", blank=True, null=True)
    read_time = RichTextField(blank=True, null=True)
    image = models.ForeignKey(
        'wagtailimages.Image', on_delete=models.SET_NULL, blank=True, null=True, related_name='+'
    )
    body = RichTextField(blank=True, null=True)
    int_section_title = RichTextField(blank=True, null=True)
    int_section_body = RichTextField(blank=True, null=True)

    def main_image(self):
        gallery_item = self.gallery_images.first()
        if gallery_item:
            return gallery_item.image
        else:
            return None

    def blogs(self):
        blogs = Page.objects.sibling_of(self).live().order_by('-first_published_at')[:3]
        return blogs


    def get_siblings(self, inclusive=True):
        siblings = Page.objects.sibling_of(self).live().order_by('-first_published_at')
        return siblings


    def prev_portrait(self):
        if self.get_prev_siblings():
            return self.get_prev_siblings()
        else:
            return self.get_siblings().last()

    def next_portrait(self):
        if self.get_next_siblings():
            return self.get_next_siblings()
        else:
            return self.get_siblings().first()


    search_fields = Page.search_fields + [
        index.SearchField('intro'),
        index.SearchField('body'),
    ]

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        FieldPanel('read_time'),
        FieldPanel('body'),
        FieldPanel('int_section_title'),
        FieldPanel('int_section_body'),
        FieldPanel('date'),
        InlinePanel('gallery_images', label="Gallery images"),
    ]



class BlogPageGalleryImage(Orderable):
    page = ParentalKey(BlogPage, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ForeignKey(
        'wagtailimages.Image', on_delete=models.SET_NULL, related_name='+',blank=True,null=True
    )
    caption = models.CharField(blank=True, max_length=250)

    panels = [
        ImageChooserPanel('image'),
        FieldPanel('caption'),
    ]