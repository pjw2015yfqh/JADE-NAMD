program main_action_angle_uni_inside
implicit none

include 'param.def'

integer n_state
integer n_traj
character(len=72) filename_ini_n
character(len=72) filename_x_p_traj
real(kind=8), allocatable, dimension(:) :: ini_n
real(kind=8), allocatable, dimension(:,:) :: x, &
                                             p, &
                                             random_1, &
                                             random_2
real(kind=8) ggamma

integer i, j, k, seed, nr
real(kind=8) angle, aaction, sigma, tmp
real(kind=8),allocatable :: random_gau(:)

write(*,*) 'n_state:'
read(*,*) n_state

write(*,*) 'n_traj:'
read(*,*) n_traj

write(*,*) 'filename of initial n(occupation):'
read(*,*) filename_ini_n

write(*,*) 'gamma:'
read(*,*) ggamma



allocate( ini_n(n_state) )
allocate( random_2(n_traj, n_state) )
allocate( x(n_traj, n_state) )
allocate( p(n_traj, n_state) )
allocate( random_1(n_traj, n_state) )
allocate( random_gau(nr) )

open(10, file=filename_ini_n)
do i = 1, n_state
  read(10, *) ini_n(i)
enddo
close(10)

CALL RANDOM_SEED()
CALL RANDOM_NUMBER(random_1)

do i = 1, n_traj
  do j = 1, n_state
    if (ini_n(j) == 0) then
      random_1(i,j) = sqrt( ggamma * ( 1.d0 + random_1(i,j) ) )
    elseif (ini_n(j) == 1) then
      random_1(i,j) = sqrt( 2.d0 + ggamma * random_1(i,j) )
    else
      write(*,*) 'Wrong "action" input! N = 1 or 0 and it cannot be the other values'
    endif
  enddo
enddo

seed = 1234567
CALL RANDOM_SEED(seed)
CALL RANDOM_NUMBER(random_2)

!open(10, file='random_gau.dat')
!do i = 1, n_traj
!  do j = 1, n_state
!    write(10,*) random_2(i,j)
!  enddo
!enddo
!close(10)

!stop

!do i = 1, n_state
!  ini_n(i) = ini_n(i) + (random_2(i) - 0.5) * 2.d0 * ggamma
!  ini_n(i) = sqrt(2.d0 * ini_n(i) + ggamma)
!enddo

do i = 1, n_traj
  do j = 1, n_state
    angle = 2* PI * random_2(i, j)
    !aaction = ini_n(j)
    aaction = random_1(i,j)
    x(i, j) = aaction * cos(angle)
    p(i, j) = aaction * sin(angle)
  enddo
enddo

!open(10, file='random_gau_2d.dat')
do i = 1, n_traj
  write(filename_x_p_traj,*) i
  filename_x_p_traj = 'traj_' // trim(adjustl(filename_x_p_traj))//'.inp'
  open(10, file=filename_x_p_traj)
  do j = 1, n_state
    write(10,9999) x(i, j), p(i, j)
  enddo
  close(10)
enddo
!close(10)


deallocate( ini_n )
deallocate( x )
deallocate( p )

9999 format(2f18.14)

end
