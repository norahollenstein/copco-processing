# -*- coding: utf-8 -*-
"""
Created on Mon Jun 18 17:43:08 2018
 Preprocessing eyetracking data
@author: LenaJaeger
"""
import numpy as np

def pix2deg(pix, screenPX,screenCM,distanceCM, adjust_origin=True):
  # Converts pixel screen coordinate to degrees of visual angle
  # screenPX is the number of pixels that the monitor has in the horizontal
  # axis (for x coord) or vertical axis (for y coord)
  # screenCM is the width of the monitor in centimeters
  # distanceCM is the distance of the monitor to the retina 
  # pix: screen coordinate in pixels
  # adjust origin: if origin (0,0) of screen coordinates is in the corner of the screen rather than in the center, set to True to center coordinates
  pix=np.array(pix)
  # center screen coordinates such that 0 is center of the screen:
  if adjust_origin: 
      pix = pix-(screenPX-1)/2 # pixel coordinates start with (0,0)
  
  # eye-to-screen-distance in pixels
  distancePX = distanceCM*(screenPX/screenCM)
  
  return np.arctan2(pix,distancePX) * 180/np.pi #  *180/pi wandelt bogenmass in grad 


#---------------------------------------------------
# Compute velocity times series from 2D position data
#---------------------------------------------------
# adapted from Engbert et al.  Microsaccade Toolbox 0.9
# x: array of shape (N,2) (x und y screen or visual angle coordinates of N samples in *chronological* order)
# returns velocity in deg/sec or pix/sec
def vecvel(x, sampling_rate=1000, smooth=True):
    N = x.shape[0]  
    v = np.zeros((N,2)) # first column for x-velocity, second column for y-velocity
    if smooth: # v based on mean of preceding 2 samples and mean of following 2 samples
        v[2:N-2, :] =  (sampling_rate/6)*(x[4:N,:] + x[3:N-1,:] - x[1:N-3,:] - x[0:N-4,:])
        # *SAMPLING => pixeldifferenz pro sec
        # v[n,:]: Differenz zwischen mean(sample_n-2, sample_n-1) und mean(sample_n+1, sample_n+2) (=> durch 2 teilen); jetzt ist aber Schrittweite 3 sample lang (von n-1.5 bis n+1.5) => durch 3 teilen => insgesamt durch 6 teilen
        # v based on preceding sample and following sample for second and penultimate sample
        v[1,:] = (sampling_rate/2)*(x[2,:] - x[0,:])
        v[N-2,:] = (sampling_rate/2)*(x[N-1,:] - x[N-3,:])
    else:  
        v[1:N-1,] = (sampling_rate/2)*(x[2:N,:] - x[0:N-2,:]) # differenz Vorgänger sample und nachfolger sample; beginnend mit 2.sample bis N
    #/2 weil dx differenz zwischen voergänger und nachfolger sample ist => schrittweite ist also 2
    return v

def get_threshold(x, sampling_rate):
    v = vecvel(x,sampling_rate=sampling_rate) 
    msdx = np.sqrt( np.nanmedian(np.power(v[:,0] - np.nanmedian(v[:,0]),2))) # median-based std of x-velocity
    msdy = np.sqrt( np.nanmedian(np.power(v[:,1] - np.nanmedian(v[:,1]),2)))
    return msdx, msdy

# compute (micro-)saccades from raw samples
# adopted from Engbert et al Microsaccade Toolbox 0.9
# von Hans Trukenbrod empfohlen fuer 1000Hz: vfac=6, mindur=6
# returns: sac, issac, radius
# sac: array of shape (7,): saccade onset, (2) saccade offset, (3) peak velocity, 
#                 (4) horizontal component (dist from first to last sample of the saccade), (5) vertical component,
#			       (6) horizontal amplitude (dist from leftmost to rightmost sample), (6) vertical amplitude
# issac: array of shape (N,): codes whether a sample of x belongs to saccade (1) or not (0)
# radius: (horizontal semi-axis of elliptic threshold; vertical semi-axis)    
# x: array of shape (N,2) (x und y screen or visual angle coordinates of N samples in *chronological* order)
# vfac:	 relative velocity threshold (same as in Microsaccades 0.9 by Engbert et al)
# mindur: minimal saccade duration
# sampling_rate: sampling frequency of the eyetracker in Hz
# threshold: if None: data-driven velocity threshold; if tuple of floats: used to compute elliptic threshold
def microsacc(x,vfac=6,min_dur=6,sampling_rate=1000, threshold=None):
  # Compute velocity
  v = vecvel(x,sampling_rate=sampling_rate) 
  if threshold: # global threshold provided
      msdx, msdy = threshold[0], threshold[1]
  else:     
      # Compute threshold from data (as Engbert et al)
      msdx = np.sqrt( np.nanmedian(np.power(v[:,0] - np.nanmedian(v[:,0]),2))) # median-based std of x-velocity
      msdy = np.sqrt( np.nanmedian(np.power(v[:,1] - np.nanmedian(v[:,1]),2)))
      assert  msdx>1e-10 # there must be enough variance in the data
      assert  msdy>1e-10
      
  radiusx = vfac*msdx # x-radius of elliptic threshold
  radiusy = vfac*msdy # y-radius of elliptic threshold
  radius = (radiusx,radiusy)
  # test if sample is within elliptic threshold
  
  test = np.power((v[:,0]/radiusx),2) + np.power((v[:,1]/radiusy),2) # test is <1 iff sample within ellipse
  indx = np.where(np.greater(test,1))[0] # indices of candidate saccades; runtime warning because of nans in test => is ok, the nans come from nans in x
    # Determine saccades
  N = len(indx) # anzahl der candidate saccades
  nsac = 0
  sac = []
  dur = 1
  a = 0 # (möglicher) begin einer saccade
  k = 0 # (möglisches) ende einer saccade, hierueber wird geloopt
  issac = np.zeros(len(x)) # codes if x[issac] is a saccade

  # Loop over saccade candidates
  while k<N-1:  # loop over candidate saccades
    if indx[k+1]-indx[k]==1: # saccade candidates, die aufeinanderfolgen
      dur = dur + 1 # erhoehe sac dur
    else:  # wenn nicht (mehr) in saccade
      # Minimum duration criterion (exception: last saccade)
      if dur>=min_dur: # schreibe saccade, sofern MINDUR erreicht wurde
        nsac = nsac + 1
        s = np.zeros(7) # entry for this saccade
        s[0] = indx[a] # saccade onset
        s[1] = indx[k] # saccade offset
        sac.append(s)    
        issac[indx[a]:indx[k]+1] = 1 # code as saccade from onset to offset        
      a = k+1 # potential onset of next saccade
      dur = 1 # reset duration  
    k = k+1
  # Check minimum duration for last microsaccade
  if  dur>=min_dur:
    nsac = nsac + 1
    s = np.zeros(7) # entry for this saccade
    s[0] = indx[a] # saccade onset
    s[1] = indx[k] # saccade offset
    sac.append(s)
    issac[indx[a]:indx[k]+1] = 1 # code as saccade from onset to offset       
  sac=np.array(sac)  
  if nsac>0:
    # Compute peak velocity, horiztonal and vertical components
    for s in range(nsac): # loop over saccades
      # Onset and offset for saccades
      a = int(sac[s,0]) # onset of saccade s
      b = int(sac[s,1]) # offset of saccade s
      idx = range(a,b+1) # indices of samples belonging to saccade s
      # Saccade peak velocity (vpeak)
      sac[s,2] = np.max(np.sqrt(np.power(v[idx,0],2) + np.power(v[idx,1],2)))
      # saccade length measured as distance between first (onset) and last (offset) sample
      sac[s,3] = x[b,0]-x[a,0] 
      sac[s,4] = x[b,1]-x[a,1] 
      # Saccade amplitude: saccade length measured as distance between leftmost and rightmost (bzw. highest and lowest) sample 
      minx = np.min(x[idx,0]) # smallest x-coordinate during saccade
      maxx = np.max(x[idx,0]) 
      miny = np.min(x[idx,1])
      maxy = np.max(x[idx,1])
      signx = np.sign(np.where(x[idx,0]==maxx)[0][0] - np.where(x[idx,0]==minx)[0][0]) # direction of saccade; np.where returns tuple; there could be more than one minimum/maximum => chose the first one
      signy = np.sign(np.where(x[idx,1]==maxy)[0][0] - np.where(x[idx,1]==miny)[0][0]) #
      sac[s,5] = signx * (maxx-minx) # x-amplitude
      sac[s,6] = signy * (maxy-miny) # y-amplitude    
  return sac, issac, radius


# same as microsacc, but returns only issac
def issac(x,vfac=6,min_dur=10,sampling_rate=1000, threshold=(10,10)): # median/mean threshold von allen texten: (9,6)
  # Compute velocity
  v = vecvel(x,sampling_rate=sampling_rate)
  if threshold: # global threshold provided
      msdx, msdy = threshold[0], threshold[1]
  else:  
      # Compute threshold
      msdx = np.sqrt( np.nanmedian(np.power(v[:,0] - np.nanmedian(v[:,0]),2))) # median-based std of x-velocity
      msdy = np.sqrt( np.nanmedian(np.power(v[:,1] - np.nanmedian(v[:,1]),2)))
      assert  msdx>1e-10 # there must be enough variance in the data
      assert  msdy>1e-10

  radiusx = vfac*msdx # x-radius of elliptic threshold
  radiusy = vfac*msdy # y-radius of elliptic threshold
  # test if sample is within elliptic threshold
  test = np.power((v[:,0]/radiusx),2) + np.power((v[:,1]/radiusy),2) # test is <1 iff sample within ellipse
  indx = np.where(np.greater(test,1))[0] # indices of candidate saccades; runtime warning because of nans in test => is ok, the nans come from nans in x
    # Determine saccades
  N = len(indx) # anzahl der candidate saccades
  dur = 1
  a = 0 # (möglicher) begin einer saccade
  k = 0 # (möglisches) ende einer saccade, hierueber wird geloopt
  issac = np.zeros(len(x)) # codes if x[issac] is a saccade
  # Loop over saccade candidates
  while k<N-1:  # loop over candidate saccades
    if indx[k+1]-indx[k]==1: # saccade candidates, die aufeinanderfolgen
      dur = dur + 1 # erhoehe sac dur
    else:  # wenn nicht (mehr) in saccade
      # Minimum duration criterion (exception: last saccade)
      if dur>=min_dur: # schreibe saccade, sofern MINDUR erreicht wurde
        issac[indx[a]:indx[k]+1] = 1 # code as saccade from onset to offset        
      a = k+1 # potential onset of next saccade
      dur = 1 # reset duration  
    k = k+1
  # Check minimum duration for last microsaccade
  if  dur>=min_dur:
    issac[indx[a]:indx[k]+1] = 1 # code as saccade from onset to offset       
  return issac


#! corruptSamples nach Sakkadenerkennung anwenden, damit Chronologie erhalten bleibt
#! es kann nach Anwendung von corruptSamples Fixationen und Sakkaden der Laenge 1 geben.
def corruptSamplesIdx(x,y, x_max, y_max, x_min, y_min, theta=0.6, samplingRate=1000):
    # x,y: x,y coordinates in degrees of visual anngle
    # x,y must be chronologically ordered sample sequences, missing values have NOT been removed yet
    # max_x... max/min coordinates for samples to fall on the screen; 
    # theta: velocity threshold in degrees/ms   
  x = np.array(x)
  y = np.array(y)
  ## Find Offending Samples
   # samples that exceed velocity threshold
  ## adjust theta depending on sampling rate
  theta=theta*1000/samplingRate
  x2 = np.append(x[0],x[:-1]) # x2 is sample that precedes x (numpy.roll not used here beacuse it inserts last element in first position)
  y2 = np.append(y[0],y[:-1]) 
  distTrv = np.sqrt(np.power((x-x2),2) + np.power((y-y2),2)) 
  fast_ix = np.where(distTrv>theta)[0] # too fast samples; np.where returns tuple
  # Missing samples
  mis_ix = np.where(np.isnan(x) | np.isnan(y))[0] # np.where returns tuple of len 1
  # samples outside the screen
  out_ix = np.where(np.greater(x, x_max) | np.greater(y, y_max) | np.greater(x_min,x) | np.greater(y_min,y))[0] 
  #RuntimeWarning: invalid value encountered in greater => is ok; comparison with nan yields nan
  # remove samples,where gaze is completely still => scheint auch recording Fehler zu sein 
  # TODO: macht das Sinn? Hiervon sind meist nur einzelne samples betroffen. erstmal raus. ggf wieder einkommentieren.
  #still_ix = np.where(np.equal(x,np.roll(x, shift=-1)) & np.equal(x,np.roll(x, shift=1)) & np.equal(y,np.roll(y, shift=-1)) & np.equal(y,np.roll(y, shift=1)))[0]
  # return all bad samples
  return np.sort(np.unique(np.concatenate((mis_ix, out_ix,fast_ix))))
