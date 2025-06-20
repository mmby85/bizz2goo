from django import forms

from ckeditor.fields import RichTextFormField
from ckeditor.widgets import CKEditorWidget
from ckeditor_uploader.fields import RichTextUploadingFormField
from ckeditor_uploader.widgets import CKEditorUploadingWidget

from .models import CKPost , Category, SubCategory
from .models import CKPost, Category, SubCategory


from django.forms import MultiWidget


class CkEditorMultiWidget(MultiWidget):
    def decompress(self, value):
        return [value for _ in self.widgets]


class CkEditorForm(forms.Form):
    ckeditor_standard_example = RichTextFormField()
    # ckeditor_upload_example = RichTextUploadingFormField(
    #     config_name="my-custom-toolbar"
    # )


class CkEditorMultiWidgetForm(forms.Form):
    SUBWIDGET_SUFFIXES = ["0", "1"]

    ckeditor_standard_multi_widget_example = forms.CharField(
        widget=CkEditorMultiWidget(
            widgets={suffix: CKEditorWidget for suffix in SUBWIDGET_SUFFIXES},
        ),
    )
    # ckeditor_upload_multi_widget_example = forms.CharField(
    #     widget=CkEditorMultiWidget(
    #         widgets={
    #             suffix: CKEditorUploadingWidget(config_name="my-custom-toolbar")
    #             for suffix in SUBWIDGET_SUFFIXES
    #         },
    #     ),
    # )


class CKPostForm(forms.ModelForm):
    class Meta:
        model = CKPost
        fields = '__all__'
        exclude = ['slug']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Filtrage dynamique des sous-catégories
        if 'category' in self.data:
            try:
                category_id = int(self.data.get('category'))
                self.fields['sub_category'].queryset = SubCategory.objects.filter(category_id=category_id).order_by('name')
            except (ValueError, TypeError):
                self.fields['sub_category'].queryset = SubCategory.objects.none()
        elif self.instance.pk and self.instance.category:
            self.fields['sub_category'].queryset = self.instance.category.subcategories.order_by('name')
        else:
            self.fields['sub_category'].queryset = SubCategory.objects.none()

        # Option par défaut pour les sous-catégories
        self.fields['sub_category'].empty_label = "Sélectionnez une sous-catégorie"

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get("category")
        sub_category = cleaned_data.get("sub_category")

        # Validation que la sous-catégorie appartient bien à la catégorie
        if sub_category and sub_category.category != category:
            self.add_error('sub_category', "La sous-catégorie ne correspond pas à la catégorie sélectionnée.")

        return cleaned_data


# class CKPostOverriddenWidgetForm(forms.ModelForm):
#     class Meta:
#         model = CKPost
#         fields = "__all__"

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#         self.fields["content"].widget = CKEditorUploadingWidget(
#             config_name="my-custom-toolbar",
#             extra_plugins=["someplugin", "anotherplugin"],
#             external_plugin_resources=[
#                 (
#                     "someplugin",
#                     "/static/path/to/someplugin/",
#                     "plugin.js",
#                 )
#             ],
#         )

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'
        # You can specify fields to exclude if needed


# blog/forms.py
from django import forms

PROFILE_CHOICES = [
    ('porteur_projet', 'Porteur de projet'),
    ('structure_accompagnement', "Structure d'accompagnement (Incubateur, Pépinière, Technopole...)"),
    ('organisme_financement', 'Organisme de financement (Banque, Micro-Finance, SICAR...)'),
]

class LeadGenerationForm(forms.Form):
    profil = forms.ChoiceField(
        choices=PROFILE_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}), # For radio buttons
        label="Profil"
    )
    email = forms.EmailField(
        label="Email *",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email *'})
    )
    nom_prenom = forms.CharField(
        label="Nom et prénom",
        required=False, # Assuming this is optional based on screenshot (no asterisk)
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom et prénom'})
    )
    telephone = forms.CharField(
        label="Téléphone",
        required=False, # Assuming optional
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Téléphone'})
    )
    gouvernorat = forms.CharField(
        label="Gouvernorat",
        required=False, # Assuming optional
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Gouvernorat'})
    )
    # You might want to add a hidden field for the source of the lead, e.g., which ad they clicked
    # source_ad_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Optional: if you want to style the radio select label differently or add a general class
        # self.fields['profil'].widget.attrs.update({'class': 'profile-radio-group'})
        # For individual radio buttons, you might need custom widget rendering or JS.
        # The default rendering of RadioSelect will create <li> or <p> tags around each input and label.
        # You'll style these in your CSS.

# --- New Form for GOZONE Contact ---
GOZONE_PROFILE_CHOICES = [
    ('porteur_projet', 'Porteur de projet'),
    ('chef_entreprise', 'Chef d’entreprise / dirigeant'),
    ('organisme_accompagnement', 'Organisme d’accompagnement (incubateur, centre de formation , etc.)'),
    ('organisme_financement', 'Organisme de financement (banque, micro-finance, SICAR , etc.)'),
    ('ong', 'Organisation Non Gouvernementale (ONG)'),
    ('professionnel', 'Professionnel (manager, ingénieur, technicien, etc.)'),
    ('expert_consultant', 'Expert / consultant / formateur'),
    ('etudiant', 'Etudiant'),
    ('autre_profil', 'Autre'),
]

GOZONE_NEEDS_CHOICES = [
    ('creation_entreprise', 'Appui à la création d’entreprise ou au montage de projet'),
    ('etudes_techniques', 'Études techniques (étude d’impact environnemental, Étude de sécurité,)'),
    ('conseil_organisationnel', 'Conseil ou accompagnement organisationnel (systèmes de management, restructuration, etc.)'),
    ('formation_professionnelle', 'Formation professionnelle sur mesure'),
    ('digitalisation_processus', 'Digitalisation de processus internes'),
    ('organisation_evenement', 'Organisation d’un événement ou atelier sur mesure'),
    ('collaboration_partenariat', 'Collaboration ou partenariat avec GOZONE'),
    ('autre_besoin', 'Autre'),
]

class GozoneContactForm(forms.Form):
    # Standard contact fields (can be shared or duplicated if styling differs greatly)
    nom_prenom = forms.CharField(
        label="Nom et Prénom*",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre nom complet'})
    )
    email = forms.EmailField(
        label="Adresse Email*",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'exemple@domaine.com'})
    )
    telephone = forms.CharField(
        label="Numéro de Téléphone (Optionnel)",
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+216 XX XXX XXX'})
    )
    organisation = forms.CharField(
        label="Organisation / Société (Optionnel)",
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de votre organisation'})
    )

    # GOZONE specific fields
    profil_gozone = forms.ChoiceField(
        choices=GOZONE_PROFILE_CHOICES,
        widget=forms.RadioSelect, # Using RadioSelect as per your description
        label="Votre profil*",
        required=True
    )
    profil_gozone_autre_details = forms.CharField(
        label="Si autre profil, veuillez préciser :",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Précisez votre profil'})
    )

    besoins_gozone = forms.MultipleChoiceField(
        choices=GOZONE_NEEDS_CHOICES,
        widget=forms.CheckboxSelectMultiple, # Using CheckboxSelectMultiple for "Cochez ou précisez"
        label="Vous êtes à la recherche de...*",
        help_text="Cochez ou précisez votre demande (Votre besoin / prestation souhaitée)",
        required=True
    )
    besoins_gozone_autre_details = forms.CharField(
        label="Si autre besoin, veuillez préciser :",
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Décrivez votre besoin spécifique'})
    )
    message_complementaire = forms.CharField(
        label="Message complémentaire (Optionnel)",
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Ajoutez des détails ou un message ici'})
    )


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # You can add common classes or tweaks here if needed
        # For radio/checkbox, styling is often template/CSS driven

    def clean(self):
        cleaned_data = super().clean()
        profil = cleaned_data.get("profil_gozone")
        profil_autre_details = cleaned_data.get("profil_gozone_autre_details")
        besoins = cleaned_data.get("besoins_gozone")
        besoins_autre_details = cleaned_data.get("besoins_gozone_autre_details")

        if profil == 'autre_profil' and not profil_autre_details:
            self.add_error('profil_gozone_autre_details', "Veuillez préciser votre profil si vous avez sélectionné 'Autre'.")

        if besoins and 'autre_besoin' in besoins and not besoins_autre_details:
            self.add_error('besoins_gozone_autre_details', "Veuillez préciser votre besoin si vous avez coché 'Autre'.")
            
        return cleaned_data