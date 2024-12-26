from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser

# Define a custom manager for the User model.
class UserManager(BaseUserManager):
    """
    A custom manager to handle the creation of users and superusers.
    """
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a user with the given email and password.
        - email: The user's email address (required).
        - password: The user's password (optional, defaults to None).
        - extra_fields: Additional fields to be set for the user (optional).
        """
        if not email:
            raise ValueError("User must have a valid email address")
        
        # Normalize the email address to a consistent format
        email = self.normalize_email(email)
        
        # Create an instance of the user model
        user = self.model(email=email, **extra_fields)
        
        # Set the user's password (hashed internally)
        user.set_password(password)
        
        # Save the user to the database
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and save a superuser with the given email and password.
        - Superuser must have is_staff=True and is_superuser=True.
        - Additional flags like is_customer and is_seller are also set to True.
        """
        # Set default fields for a superuser
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_customer', True)
        extra_fields.setdefault('is_seller', True)

        # Ensure required superuser flags are properly set
        if not extra_fields['is_staff']:
            raise ValueError("Superuser must have is_staff=True.")
        if not extra_fields['is_superuser']:
            raise ValueError("Superuser must have is_superuser=True.")

        # Use the create_user method to create a superuser
        return self.create_user(email, password, **extra_fields)

# Define a custom User model by extending AbstractBaseUser.
class User(AbstractBaseUser):
    """
    A custom User model that uses email instead of username for authentication.
    """
    # User fields
    email = models.EmailField(max_length=255, unique=True)  # Email is the unique identifier
    name = models.CharField(max_length=255,blank=True)  # User's full name
    city = models.CharField(max_length=255, blank=True, null=True)  # Optional city field
    is_active = models.BooleanField(default=True)  # Indicates if the user is active
    is_staff = models.BooleanField(default=False)  # Indicates if the user has staff privileges
    is_superuser = models.BooleanField(default=False)  # Indicates if the user is a superuser
    is_customer = models.BooleanField(default=True)  # Custom field to track if the user is a customer
    is_seller = models.BooleanField(default=False)  # Custom field to track if the user is a seller
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for user creation
    updated_at = models.DateTimeField(auto_now=True)  # Timestamp for the last update

    # Specify the unique identifier for authentication
    USERNAME_FIELD = 'email'

    # Fields required when creating a superuser (besides USERNAME_FIELD)
    REQUIRED_FIELDS = ['name']

    # Use the custom manager for this model
    objects = UserManager()

    class Meta:
        """
        Meta options for the User model.
        - verbose_name: Human-readable singular name for the model.
        - verbose_name_plural: Human-readable plural name for the model.
        """
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        """
        String representation of the user.
        - Returns the email address as the representation.
        """
        return self.email

    def has_perm(self, perm, obj=None):
        """
        Check if the user has a specific permission.
        - Only superusers have all permissions.
        """
        return self.is_superuser

    def has_module_perms(self, app_label):
        """
        Check if the user has permissions to view the app identified by `app_label`.
        - Only superusers have access to all apps.
        """
        return self.is_superuser
