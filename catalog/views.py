from django.shortcuts import render
from catalog.models import Book, Author, BookInstance, Genre
# Create your views here.
from django.contrib.auth.decorators import login_required

@login_required()
def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    # The 'all()' is implied by default.
    num_authors = Author.objects.count()
    #Books and genres contains particular word insensitive
    num_genres_with_ern = Genre.objects.filter(name__icontains='ern').count()
    num_books_with_er = Book.objects.filter(title__icontains='er').count()
    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_genres_with_ern': num_genres_with_ern,
        'num_books_with_er': num_books_with_er,
        'num_visits': num_visits,
    }
    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)

from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin

class BookListView(LoginRequiredMixin, generic.ListView):
    model = Book
    paginate_by = 10


class BookDetailView(LoginRequiredMixin ,generic.DetailView):
    model = Book


class AuthorListView(LoginRequiredMixin, generic.ListView):
    model = Author
    paginate_by = 5

class AuthorDetailView(LoginRequiredMixin, generic.DetailView):
    model = Author

class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    '''Generic class based view listing books on loan to current user. '''
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower = self.request.user).filter(status__exact='o').order_by('due_back')



from django.contrib.auth.mixins import PermissionRequiredMixin


class LoanedBooksAllListView(PermissionRequiredMixin, generic.ListView):
    '''Generic class based view listing books on loan to current user. '''
    model = BookInstance
    permission_required = 'can_mark_returned'
    template_name = 'catalog/bookinstance_list_all_borrowed.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')


import datetime
from catalog.forms import RenewBookForm
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import permission_required

@permission_required('can_mark_returned')
def renew_book_librarian(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)

    #If this is a POST request then  process the form data
    if request.method == 'POST':
        # Create a form and populate it with user entered data
        form = RenewBookForm(request.POST)

        #Check if the form is valid
        if form.is_valid():
            # Process the data in form.cleaned_data as required (Here we just write to the model due_back field)
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()
            #redirect to a new URL
            return HttpResponseRedirect(reverse('all-borrowed'))
    # If this is a GET (or any other method) create the default form
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)


# from django.forms import ModelForm
# from catalo.models import BookInstance
#
# or class RenewBookModelForm(ModelForm):
#       def clean_due_back(self):
#           if request.method == 'POST':
#               data = self.cleaned_data['due_back']
#               if data < datetime.date.today():
#                   raise ValidationError(_('Invalid date - renewaal in past'))
#               if data > datetime.date() + datetime.timedelta(weeks=4):
#                   raise ValidationError(_('Invalid date - renewal more than 4 weeks ahead'))
#               return data
#           else:
#               form = RenewBookForm(initial={'due_back':proposed_renewal_date})
#       class meta
#           model = BookInstance
#           fields = ['due_back']
#           labels = {'due_back':_('New renewal Date')}
#           help_texts = {'due_back':_('Enter a date between now and 4 weeks(default 3).')}

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from catalog.models import Author
from django.contrib.auth.mixins import PermissionRequiredMixin

class AuthorCreateView(PermissionRequiredMixin, CreateView):
    model = Author
    fields = '__all__'
    permission_required = 'catalog.can_mark_returned'
    initial = {'date_of_death': '05/01/2020'}

class AuthorUpdateView(PermissionRequiredMixin, UpdateView):
    model = Author
    permission_required = 'catalog.can_mark_returned'
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']

class AuthorDeleteView(PermissionRequiredMixin, DeleteView):
    model = Author
    permission_required = 'catalog.can_mark_returned'
    success_url = reverse_lazy('authors')

class BookCreateView(PermissionRequiredMixin, CreateView):
    model = Book
    fields = '__all__'
    permission_required = 'catalog.can_mark_returned'

class BookUpdateView(PermissionRequiredMixin, UpdateView):
    model = Book
    permission_required = 'catalog.can_mark_returned'
    fields = ['title', 'author', 'summary', 'isbn','genre']

class BookDeleteView(PermissionRequiredMixin, DeleteView):
    model = Book
    permission_required = 'catalog.can_mark_returned'
    success_url = reverse_lazy('books')

