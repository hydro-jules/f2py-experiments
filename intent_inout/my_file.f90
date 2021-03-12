subroutine add_scalar(an_array, a_scalar)

    implicit none

    real, intent(inout), dimension(:) :: an_array
    real, intent(in) :: a_scalar

    an_array(:) = an_array(:) + a_scalar

end subroutine add_scalar  

subroutine add_scalar_in_out(n, an_array, a_scalar)

    implicit none

    integer, intent(in) :: n
    real, intent(inout), dimension(n) :: an_array
    !f2py intent(in,out) an_array
    real, intent(in) :: a_scalar

    an_array(:) = an_array(:) + a_scalar

end subroutine add_scalar_in_out 

subroutine add_scalar_inplace(n, an_array, a_scalar)

    implicit none

    integer, intent(in) :: n
    real, intent(inout), dimension(n) :: an_array
    !f2py intent(inplace) an_array
    real, intent(in) :: a_scalar

    an_array(:) = an_array(:) + a_scalar

end subroutine add_scalar_inplace  
