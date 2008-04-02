import numpy

def do_bg_maint( running_mean_im,
                 hw_roi_frame,
                 max_frame_size,
                 ALPHA,
                 running_mean8u_im,
                 fastframef32_tmp,
                 running_sumsqf,
                 mean2,
                 std2,
                 running_stdframe,
                 n_sigma,
                 compareframe8u,
                 bright_non_gaussian_cutoff,
                 noisy_pixels_mask,
                 bright_non_gaussian_replacement,
                 bench=0):
    """
    = Arguments =

    FastImage.FastImage32f running_mean_im   IO - current estimate of mean of x
    FastImage.FastImage8u hw_roi_frame       Input - current image
    FastImage.Size max_frame_size            Input - size of all images
    float ALPHA                              Input
    FastImage.FastImage8u running_mean8u_im  Output
    FastImage.FastImage32f fastframef32_tmp  Output (temp/scratch)
    FastImage.FastImage32f running_sumsqf    IO - current estimate of mean of x^2
    FastImage.FastImage32f mean2             Output - running_mean_im^2
    FastImage.FastImage32f std2              Output - running_sumsqf-mean2
    FastImage.FastImage32f running_stdframe  Output - sqrt(std2)
    float n_sigma                            Input
    FastImage.FastImage8u compareframe8u     Output
    int bright_non_gaussian_cutoff           Input
    FastImage.FastImage8u noisy_pixels_mask  Input
    int bright_non_gaussian_replacement      Input
    int bench                                Input

    = Returns =
    Benchmarking information if bench != 0

    """

    hw_roi_frame = numpy.asarray( hw_roi_frame )
    running_mean_im = numpy.asarray( running_mean_im )
    running_mean8u_im = numpy.asarray( running_mean8u_im )
    fastframef32_tmp = numpy.asarray( fastframef32_tmp )
    running_sumsqf = numpy.asarray( running_sumsqf )
    mean2 = numpy.asarray( mean2 )
    std2 = numpy.asarray( std2 )
    running_stdframe = numpy.asarray( running_stdframe )
    compareframe8u = numpy.asarray( compareframe8u )

    # maintain running average
    # <x>
    running_mean_im[:,:] = (1-ALPHA)*running_mean_im + ALPHA*hw_roi_frame

    running_mean8u_im[:,:] = running_mean_im.astype( numpy.uint8 )

    # standard deviation calculation
    fastframef32_tmp[:,:] = hw_roi_frame

    # x^2
    fastframef32_tmp[:,:] = fastframef32_tmp**2

    # <x^2>
    running_sumsqf[:,:] = (1-ALPHA)*running_sumsqf + ALPHA*fastframef32_tmp

    ### GETS SLOWER
    # <x>^2
    mean2[:,:] = running_mean_im**2

    # <x^2> - <x>^2
    std2[:,:] = running_sumsqf - mean2

    # sqrt( |<x^2> - <x>^2| )
    # clip
    running_stdframe[:,:] = abs(std2)
    running_stdframe[:,:] = numpy.sqrt( running_stdframe )

    # now create frame for comparison
    if n_sigma != 1.0:
        running_stdframe[:,:] = n_sigma*running_stdframe

    # XXX TODO: currently this ignores mask and non_gaussian stuff
    compareframe8u[:,:] = running_stdframe.round()

