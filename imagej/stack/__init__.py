import xarray as xr

def combine_channels(channel_1, channel_2):
    """
    Combine two channels into a new xarray.DataArray.
    :param channel_1: First channel to combine.
    :param channel_2: Second channel to combine.
    :return: Combined channels as new xarray.DataArray.
    """
    combined_img = xr.concat([channel_1[:,:,:], channel_2[:,:,:]], dim='Channel')
    combined_img = combined_img.rename('merged')

    return combined_img

def delete_channel(stack, channel_number: int):
    """
    Delete a specified channel from a stack.
    """
    if len(stack.dims) == 4:
        # TODO: Logic for 4D data
        return None
    elif len(stack.dims) == 3:
        if channel_number == 1:
            extract = stack[:,:,1:]
            return extract
        else:
            channel_temp = channel_number - 1
            extract_1 = stack[:,:,:channel_temp]
            extract_2 = stack[:,:,channel_temp + 1:]
            combined_extract = combine_channels(extract_1, extract_2)
            return combined_extract

def extract_channel(stack, channel_number: int):
    """
    Extract a specified channel from a stack.
    :param stack: Input stack.
    :param channel_number: Channel number to extract.
    :return: A new xarray.DataArray with a single channel.
    """
    channel_temp = channel_number - 1

    if len(stack.dims) == 4:
        extract = stack[:,channel_temp,:,:]
        extract = extract.expand_dims('Channel') # re-attach the Channel coordinate with the Channel dimension
        extract = extract.rename("Channel " + str(channel_number))
        print(f"Extracted channel {str(channel_number)}.")
    elif len(stack.dims) == 3:
        extract = stack[:,:,channel_temp]
        extract = extract.expand_dims('Channel') # re-attach the Channel coordinate with the Channel dimension
        extract = extract.rename("Channel " + str(channel_number))
        extract = extract.transpose('y', 'x', 'Channel')
    else:
        print(f"No channels found: {stack.dims}")

    return extract