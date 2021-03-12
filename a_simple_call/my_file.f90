subroutine add_scalar(n, an_array, a_scalar, the_result)

    implicit none

    integer, intent(in) :: n
    real, intent(in), dimension(n) :: an_array
    real, intent(in) :: a_scalar
    real, intent(out), dimension(n) :: the_result

    the_result(:) = an_array(:) + a_scalar

end subroutine add_scalar    

subroutine add_array(n, array_one, array_two, the_result)

    implicit none

    integer, intent(in) :: n
    real, intent(in), dimension(n) :: array_one, array_two
    real, intent(out), dimension(n) :: the_result

    the_result(:) = array_one(:) + array_two(:)

end subroutine add_array
