import xarray as xr

def combine_channels(channel_1, channel_2):
    """
    Combine two channels into a new xarray.DataArray.
    :param channel_1: First channel to combine.
    :param channel_2: Second channel to combine.
    :return: Combined channels as new xarray.DataArray.
    """
    combined_img = xr.concat([channel_1, channel_2], dim='Channel')
    return combined_img.rename('merged')

def concatenate_frames(frame_1, frame_2):
    """
    Concatenate two xarray.DataArrays along the 'Time' dimension.
    :param frame_1: The first xarray.DataArray to concatenate.
    :param frame_2: The second xarray.DataArray to concatenate.
    """
    if len(frame_1.dims) == 4 and len(frame_2.dims) == 4:
        concatenated_frames = xr.concat([frame_1, frame_2], dim='Time')
        return concatenated_frames.rename('concatenated')
    else:
        print(f"No time dimension found.\nframe_1: {frame_1.coords}\nframe_2: {frame_2.coords}")
    

def delete_channel(stack, channel_number: int):
    """
    Delete a specified channel from a stack.
    :param stack: Input stack.
    :param channel_number: Channel number to delete.
    """
    channel_temp = channel_number - 1

    if len(stack.dims) == 4: # ('Time', 'Channel',  'y', 'x')
        if channel_number == 1:
            extract = stack[:,1:,:,:]
            return extract
        else:
            extract_1 = stack[:,:channel_temp,:,:]
            extract_2 = stack[:,channel_temp + 1:,:,:]
            combined_extract = combine_channels(extract_1, extract_2)
            return combined_extract
    elif len(stack.dims) == 3: # ('y', 'x', 'Channel')
        if channel_number == 1:
            extract = stack[:,:,1:]
            return extract
        else:
            extract_1 = stack[:,:,:channel_temp]
            extract_2 = stack[:,:,channel_temp + 1:]
            combined_extract = combine_channels(extract_1, extract_2)
            return combined_extract
    else:
        print(f"No channels found: {stack.dims}")

def delete_frames(stack, first_frame:int, last_frame:int, step=1):
    """
    Delete frames in the specified range.
    """
    first_frame_temp = first_frame - 1

    if len(stack.dims) == 4 and 'Time' in stack.coords:
        extract_1 = stack[:first_frame_temp:step,:,:,:]
        extract_2 = stack[last_frame::step,:,:,:]
        concatenated_extract = concatenate_frames(extract_1, extract_2)
        return concatenated_extract
    else:
        print(f"No time dimension found: {stack.dims}")

def extract_frame(stack, frame_number):
    """
    Extract a single frame from a stack.
    :param stack: Input stack.
    :param frame_number: The number to extract.
    """
    frame_number_temp = frame_number - 1

    if len(stack.dims) == 4 and 'Time' in stack.coords:
        extract = stack[frame_number_temp:frame_number,:,:,:]
        return extract
    else:
        print(f"No time dimension found: {stack.dims}")

def extract_frames(stack, first_frame:int, last_frame:int, step=1):
    """
    Extract a specified frame range (first and last frame values are kept).
    :param stack: Input stack.
    :param first_frame: First frame of range to extract.
    :param last_frame: Last frame of range to extract.
    :param step: Step pattern of frame range to extract.
    """
    first_frame_temp = first_frame - 1

    if len(stack.dims) == 4 and 'Time' in stack.coords:
        extract = stack[first_frame_temp:last_frame:step,:,:,:]
        return extract
    else:
        print(f"No time dimension found: {stack.dims}")

def extract_channel(stack, channel_number: int):
    """
    Extract a specified channel from a stack.
    :param stack: Input stack.
    :param channel_number: Channel number to extract.
    :return: A new xarray.DataArray with a single channel.
    """
    channel_temp = channel_number - 1

    if len(stack.dims) == 4: # ('Time', 'Channel',  'y', 'x')
        extract = stack[:,channel_temp,:,:]
        extract = extract.expand_dims('Channel') # re-attach the Channel coordinate with the Channel dimension
        extract = extract.rename("Channel " + str(channel_number))
        return extract
    elif len(stack.dims) == 3: # ('y', 'x', 'Channel')
        extract = stack[:,:,channel_temp]
        extract = extract.expand_dims('Channel') # re-attach the Channel coordinate with the Channel dimension
        extract = extract.rename("Channel " + str(channel_number))
        extract = extract.transpose('y', 'x', 'Channel')
        return extract
    else:
        print(f"No channels found: {stack.dims}")