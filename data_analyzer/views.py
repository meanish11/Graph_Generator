# data_analyzer/views.py - Update and add these views
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from .models import ExcelFile
from .forms import ExcelUploadForm, CustomLoginForm, CustomSignupForm
from .utils import extract_headers_and_data, get_excel_sheets, create_plot
import json

def index(request):
    return redirect('visualize_data')

@login_required
def upload_file(request):
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = form.save(commit=False)
            excel_file.uploaded_by = request.user
            excel_file.save()
            messages.success(request, 'File uploaded successfully!')
            return redirect('file_list')
        else:
            messages.error(request, 'Error uploading file. Please check the form.')
    else:
        form = ExcelUploadForm()
    
    try:
        # Show only files uploaded by the current user
        files = ExcelFile.objects.filter(uploaded_by=request.user).order_by('-uploaded_at')
    except Exception as e:
        files = []
        messages.warning(request, 'Unable to retrieve files.')
    
    return render(request, 'upload.html', {'form': form, 'files': files})

@login_required
def file_list(request):
    try:
        # Show only files uploaded by the current user
        files = ExcelFile.objects.filter(uploaded_by=request.user).order_by('-uploaded_at')
    except Exception as e:
        files = []
        messages.error(request, 'Unable to retrieve files.')
    
    return render(request, 'file_list.html', {'files': files})

@login_required
def delete_file(request, pk):
    try:
        # Ensure user can only delete their own files
        file = get_object_or_404(ExcelFile, pk=pk, uploaded_by=request.user)
        file_name = file.name
        file.delete()
        messages.success(request, f'File "{file_name}" deleted successfully!')
    except Exception as e:
        messages.error(request, f'Error deleting file: {str(e)}')
    
    return redirect('file_list')

def visualize_data(request):
    try:
        # Show all public files for visualization
        files = ExcelFile.objects.filter(is_public=True)
    except Exception as e:
        files = []
        messages.warning(request, 'Unable to retrieve files.')
    
    selected_file_id = request.GET.get('file_id')
    
    context = {
        'files': files,
        'selected_file_id': selected_file_id
    }
    
    return render(request, 'visualize.html', context)

def signup_view(request):
    if request.method == 'POST':
        form = CustomSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('upload_file')
    else:
        form = CustomSignupForm()
    return render(request, 'signup.html', {'form': form})

class CustomLoginView(LoginView):
    form_class = CustomLoginForm
    template_name = 'login.html'
    
    def form_valid(self, form):
        messages.success(self.request, f'Welcome back, {form.get_user().username}!')
        return super().form_valid(form)

def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('visualize_data')

# Keep all other existing views (get_sheets, get_columns, plot_graph, export_graph) the same
# ... rest of the views remain unchanged ...

@csrf_exempt
def get_sheets(request):
    file_id = request.GET.get('file_id')
    if file_id:
        try:
            excel_file = get_object_or_404(ExcelFile, pk=file_id)
            sheets = get_excel_sheets(excel_file.file.path)
            return JsonResponse({'sheets': sheets})
        except Exception as e:
            return JsonResponse({'error': str(e), 'sheets': []})
    return JsonResponse({'sheets': []})

# data_analyzer/views.py - Update the get_columns function

# data_analyzer/views.py - Update the get_columns function

@csrf_exempt
def get_columns(request):
    file_id = request.GET.get('file_id')
    sheet_name = request.GET.get('sheet_name')
    
    if file_id and sheet_name:
        try:
            excel_file = get_object_or_404(ExcelFile, pk=file_id)
            data = extract_headers_and_data(excel_file.file.path, sheet_name)
            
            if data and data['columns']:
                return JsonResponse({
                    'headers_info': data['headers_info'],
                    'columns': data['columns'],
                    'x_columns': data.get('x_columns', []),
                    'y_columns': data.get('y_columns', []),
                    'first_header': data.get('first_header', '')
                })
        except Exception as e:
            print(f"Error in get_columns: {e}")
            return JsonResponse({
                'error': str(e), 
                'headers_info': {}, 
                'columns': [], 
                'x_columns': [],
                'y_columns': [],
                'first_header': ''
            })
    
    return JsonResponse({
        'headers_info': {}, 
        'columns': [], 
        'x_columns': [],
        'y_columns': [],
        'first_header': ''
    })
@csrf_exempt
def plot_graph(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            file_id = data.get('file_id')
            sheet_name = data.get('sheet_name')
            x_column = data.get('x_column')
            y_columns = data.get('y_columns')
            plot_type = data.get('plot_type')
            
            excel_file = get_object_or_404(ExcelFile, pk=file_id)
            excel_data = extract_headers_and_data(excel_file.file.path, sheet_name)
            
            if excel_data:
                fig_json = create_plot(
                    excel_data['data'], 
                    x_column, 
                    y_columns, 
                    plot_type,
                    f"{excel_file.name} - {sheet_name}"
                )
                return JsonResponse({'figure': fig_json})
        except Exception as e:
            return JsonResponse({'error': str(e)})
    
    return JsonResponse({'error': 'Invalid request'})

# data_analyzer/views.py - Add/Update these functions

# data_analyzer/views.py - Add this function

@csrf_exempt
def export_graph(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            fig_json = data.get('figure')
            format = data.get('format', 'pdf')
            
            if not fig_json:
                return JsonResponse({'error': 'No figure data provided'}, status=400)
            
            # Export using plotly
            import plotly.graph_objects as go
            import plotly.io as pio
            
            fig = go.Figure(json.loads(fig_json))
            
            if format == 'pdf':
                image_bytes = pio.to_image(fig, format='pdf', width=1200, height=800)
                response = HttpResponse(image_bytes, content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename="graph.pdf"'
            elif format == 'jpg':
                image_bytes = pio.to_image(fig, format='jpg', width=1200, height=800)
                response = HttpResponse(image_bytes, content_type='image/jpeg')
                response['Content-Disposition'] = 'attachment; filename="graph.jpg"'
            else:
                return JsonResponse({'error': 'Invalid format specified'}, status=400)
            
            return response
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)