module my_module

    implicit none

    real, dimension(:), allocatable :: my_array

    contains
    
        subroutine allocate_memory(n)
            implicit none

            integer, intent(in) :: n

            if (.not. allocated(my_array)) allocate(my_array(n))
            
            my_array(:) = 0.0

        end subroutine allocate_memory    
    
        subroutine add_scalar(a_scalar)
        
            implicit none

            real, intent(in) :: a_scalar

            my_array(:) = my_array(:) + a_scalar

        end subroutine add_scalar    

end module my_module
