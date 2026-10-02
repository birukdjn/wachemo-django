from typing import List, Optional
from django.contrib.auth.models import User
from student.models import Student

class ParentService:
    @staticmethod
    def get_linked_children(parent_user: User) -> List[Student]:
        """
        Returns only children explicitly linked to the specified parent user.
        Strictly prevents fallback to arbitrary unlinked students.
        """
        if not parent_user or not parent_user.is_authenticated:
            return []
        return list(Student.objects.filter(parent=parent_user).select_related('user', 'department'))

    @staticmethod
    def get_selected_child(parent_user: User, requested_student_id: Optional[str] = None) -> Optional[Student]:
        """
        Retrieves requested child if linked to parent_user, or defaults to first linked child.
        Returns None if parent has no linked children.
        """
        children = ParentService.get_linked_children(parent_user)
        if not children:
            return None
            
        if requested_student_id:
            for child in children:
                if str(child.id) == str(requested_student_id) or child.student_id == str(requested_student_id):
                    return child
                    
        return children[0]
