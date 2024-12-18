from django.test import TestCase
from .models import Post
from django.contrib.auth.models import User
from django.shortcuts import reverse

class PostTest(TestCase):
    def setUp(self) :
      self.user = User.objects.create(username='user1')
      self.post1 = Post.objects.create(
          author = self.user,
          title = 'title for post1',
          text = 'description for post1',
          status = Post.CHOICES[0][0] #pub
      )
      
      self.post2 = Post.objects.create(
          author = self.user,
          title = 'title for post2',
          text = 'description for post2',
          status = Post.CHOICES[1][0] #pub
      )
      
    def test_str_of_model_post(self):
        post = self.post1
        self.assertEqual(str(post), post.title)

    def test_post_detail(self):
        self.assertEqual(self.post1.author, self.user)
        self.assertEqual(self.post1.title, 'title for post1')
        self.assertEqual(self.post1.text, 'description for post1')
        self.assertEqual(self.post1.status, Post.CHOICES[0][0])
        self.assertEqual(self.post2.status, Post.CHOICES[1][0])
    
    def test_index_url(self):
        response = self.client.get('/')    
        self.assertEqual(response.status_code, 200)
        
    def test_index_url_by_name(self):
        response = self.client.get(reverse('blog_index'))
        self.assertEqual(response.status_code, 200)
        
    def test_the_post1_is_exist_on_listpage(self):
        response = self.client.get(reverse('blog_index'))  
        self.assertContains(response, 'title for post1')  
        
    def test_post_detail_url(self):
        response = self.client.get(f'/blog/{self.post1.pk}/')
        self.assertEqual(response.status_code, 200)
                   
    def test_post_detil_url_by_name(self):
        response = self.client.get(reverse('post_detail',args=[self.post1.id]))
        self.assertEqual(response.status_code, 200)                   
        
    def test_post_detail_on_detail_page(self):
        response = self.client.get(f'/blog/{self.post1.id}/')    
        self.assertContains(response, self.post1.text) 
        
    def test_status_404_if_post_id_not_exist(self):
        response = self.client.get(reverse('post_detail', args=[self.post1.id + 1000]))
        self.assertEqual(response.status_code, 404)               
        
    def test_not_show_post_if_it_is_draft(self):
        response = self.client.get(reverse('blog_index'))
        self.assertContains(response, self.post1.title)
        self.assertNotContains(response, self.post2.title)        
        
    def test_post_create_view(self):
        response = self.client.post(reverse('post_create'),{
            'title' : 'some title',
            'text': 'some text',
            'status' : 'pub',
            'author' :self.user.pk
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Post.objects.last().title, 'some title')
        self.assertEqual(Post.objects.last().text, 'some text')        
        
    def test_post_update_view(self) :
        response = self.client.post(reverse('post_update',args=[self.post2.id]),{
            'title' : 'some title update',
            'text': 'some text update',
            'status' : 'pub',
            'author' : self.post2.author.id,
            
            })
        self.assertEqual(response.status_code, 302)   
        
        
    def test_post_delete_view(self):
        resopnse = self.client.post(reverse('post_delete', args=[self.post1.pk]),)
        self.assertEqual(resopnse.status_code, 302)             