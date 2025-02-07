from django.core.management.base import BaseCommand
from django.conf import settings
import pinecone

class Command(BaseCommand):
    help = 'Initialize Pinecone index for music similarity search'

    def handle(self, *args, **kwargs):
        try:
            pinecone.init(
                api_key=settings.PINECONE_API_KEY,
                environment=settings.PINECONE_ENV
            )

            # Create index if it doesn't exist
            if settings.PINECONE_INDEX not in pinecone.list_indexes():
                pinecone.create_index(
                    name=settings.PINECONE_INDEX,
                    dimension=2048,  # CLMR embedding dimension
                    metric='cosine'
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created index {settings.PINECONE_INDEX}')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(f'Index {settings.PINECONE_INDEX} already exists')
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error initializing Pinecone: {str(e)}')
            ) 