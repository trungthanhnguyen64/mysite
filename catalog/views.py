import datetime
import uuid
from django.shortcuts import render
from .models import Book, Author, BookInstance, Genre
from django.views import generic
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from catalog.forms import RenewBookForm
from django.contrib.auth.decorators import login_required, permission_required
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

class BookListView(generic.ListView):
    model = Book
    paginate_by = 2

class BookDetailView(generic.DetailView):
    model = Book

def book_detail_view(request, primary_key):
    book = get_object_or_404(Book, pk=primary_key)
    return render(request, 'catalog/book_detail.html', context={'book': book})

class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 10

class AuthorDetailView(generic.DetailView):
    model = Author

    def get_context_data(self, **kwargs):
        context = super(AuthorDetailView, self).get_context_data(**kwargs)
        context['books'] = context['author'].book_set.all()
        return context

def author_detail_view(request, primary_key):
    author = get_object_or_404(Author, pk=primary_key)
    return render(request, 'catalog/auhtor_detail.html', context={'author': author})

def index(request):
    """View function for home page of site"""

    # Generate counts of the main objects
    num_books = Book.objects.count()
    num_instances = BookInstance.objects.count()
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()# Available books (status = 'a')
    num_authors = Author.objects.count()
    
    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1
    
    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_visits': num_visits,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)

class LoanedBooksByUserListView(LoginRequiredMixin, PermissionRequiredMixin, generic.ListView):
    model = BookInstance
    template_name = "catalog/bookinstance_list_borrowed_user.html"
    permission_required = "catalog.can_mark_returned"
    paginate_by = 10

    def get_queryset(self):
        return (
            BookInstance.objects.filter(borrower=self.request.user, status__exact="o")
            .order_by("-due_back")
        )

@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
    """View function for renewing a specific BookInstance by librarian."""
    book_instance = get_object_or_404(BookInstance, pk=pk)
    
    # If this is a POST request then process the Form data
    if request.method == 'POST':
        form = RenewBookForm(request.POST)
        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the modeldue_back field)
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            return HttpResponseRedirect(reverse('my-borrowed') )
    
    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})
    
    context = {
        'form': form,
        'book_instance': book_instance,
    }
    return render(request, 'catalog/book_renew_librarian.html', context)

class AuthorCreate(CreateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death', 'biography']
    initial = {'date_of_death': '11/06/2020'}

class AuthorUpdate(UpdateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death', 'biography']

class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('authors')

