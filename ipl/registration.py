#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @author Vladimir S. FONOV
# @date 29/06/2015
#
# registration tools


from __future__ import print_function

import os
import sys
import shutil
import tempfile
import subprocess
import re
import fcntl
import traceback
import collections
import math
import argparse
# local stuff
import minc_tools


# hack to make it work on Python 3
try:
    unicode = unicode
except NameError:
    # 'unicode' is undefined, must be Python 3
    str = str
    unicode = str
    bytes = bytes
    basestring = (str,bytes)
else:
    # 'unicode' exists, must be Python 2
    str = str
    unicode = unicode
    bytes = str
    basestring = basestring
    
    
    
linear_registration_config={
    'bestlinreg': [
              {  "blur"       : "blur",
                  "trans"      : ['-est_translations'],
                  "blur_fwhm"  : 16,
                  "steps"      : [8, 8, 8],
                  "tolerance"  : 0.01,
                  "simplex"    : 32 },

              {  "blur"       : "blur",
                  "trans"      : None,
                  "blur_fwhm"  : 8,
                  "steps"      : [4, 4, 4],
                  "tolerance"  : 0.004,
                  "simplex"    : 16 },

              {  "blur"       : "blur",
                  "trans"      : None,
                  "blur_fwhm"  : 4,
                  "steps"      : [4, 4, 4],
                  "tolerance"  : 0.004,
                  "simplex"    : 8 },

              { "blur"       : "dxyz",
                  "trans"      : None,
                  "blur_fwhm"  : 8,
                  "steps"      : [4, 4, 4],
                  "tolerance"  : 0.004,
                  "simplex"    : 4 },

              {  "blur"       : "dxyz",
                  "trans"      : None,
                  "blur_fwhm"  : 4,
                  "steps"      : [4, 4, 4],
                  "tolerance"  : 0.004,
                  "simplex"    : 2 }
          ],
              
     'bestlinreg_s': [
            { "blur"        : "blur",
                "trans"       : ['-est_translations'],
                "blur_fwhm"   : 16,
                "steps"       : [8,8,8],
                "tolerance"   : 0.01,
                "simplex"     : 32 },

            { "blur"        : "blur",
                "trans"       : None,
                "blur_fwhm"   : 8,
                "steps"       : [4,4,4],
                "tolerance"   : 0.004,
                "simplex"     : 16 },

            { "blur"        : "blur",       
                "trans"       : None,
                "blur_fwhm"   : 8,
                "steps"       : [4,4,4],
                "tolerance"   : 0.0001,
                "simplex"     : 16 },

            { "blur"        : "blur",
                "trans"       : None,
                "blur_fwhm"   : 4,
                "steps"       : [4,4,4],
                "tolerance"   : 0.0001,
                "simplex"     : 8 },

            { "blur"        : "blur",
                "trans"       : None,
                "blur_fwhm"   : 2,
                "steps"       : [2,2,2],
                "tolerance"   : 0.0005,
                "simplex"     : 4 }         
         ],
            
     'bestlinreg_s2': [
            { "blur"        : "blur",
                "trans"       : ['-est_translations'],
                "blur_fwhm"   : 16,
                "steps"       : [8,8,8],
                "tolerance"   : 0.01,
                "simplex"     : 32 },

            { "blur"        : "blur",
                "trans"       : None,
                "blur_fwhm"   : 8,
                "steps"       : [4,4,4],
                "tolerance"   : 0.004,
                "simplex"     : 16 },

            { "blur"        : "blur",
                "trans"       : None,
                "blur_fwhm"   : 4,
                "steps"       : [4,4,4],
                "tolerance"   : 0.004,
                "simplex"     : 8 },

            { "blur"        : "dxyz",
                "trans"       : None,
                "blur_fwhm"   : 8,
                "steps"       : [4,4,4],
                "tolerance"   : 0.004,
                "simplex"     : 4 },

            { "blur"        : "dxyz",
                "trans"       : None,
                "blur_fwhm"   : 4,
                "steps"       : [4,4,4],
                "tolerance"   : 0.004,
                "simplex"     : 2 }
         ],
            
     'experiment_1': [
            { "blur"        : "blur",
                "trans"       : ['-est_translations'],
                "blur_fwhm"   : 8,
                "steps"       : [8,8,8],
                "tolerance"   : 0.01,
                "simplex"     : 32 },

            { "blur"        : "blur",
                "trans"       : None,
                "blur_fwhm"   : 8,
                "steps"       : [4,4,4],
                "tolerance"   : 0.004,
                "simplex"     : 16 },

            { "blur"        : "blur",
                "trans"       : None,
                "blur_fwhm"   : 4,
                "steps"       : [4,4,4],
                "tolerance"   : 0.004,
                "simplex"     : 8 },

            { "blur"        : "dxyz",
                "trans"       : None,
                "blur_fwhm"   : 8,
                "steps"       : [4,4,4],
                "tolerance"   : 0.004,
                "simplex"     : 4 },

            { "blur"        : "dxyz",
                "trans"       : None,
                "blur_fwhm"   : 4,
                "steps"       : [4,4,4],
                "tolerance"   : 0.004,
                "simplex"     : 2 }
         ],
            
    'bestlinreg_new': [      # re-imelementation from Claude's bestlinreg ~ 2016-12-01
        {   'blur'        : "blur",       # -lsq7 scaling only
            'parameters'  : "-lsq6",
            'trans'       : ['-est_translations'],
            'blur_fwhm'   : 8,
            'steps'       : [4, 4, 4],
            'tolerance'   : 0.0001,
            'simplex'     : 16 },

        {   'blur'        : "blur",       # -lsqXX full options
            'parameters'  : "-lsq7",
            'trans'       : None,
            'blur_fwhm'   : 8,
            'steps'       : [4, 4, 4],
            'tolerance'   : 0.0001,
            'simplex'     : 16 },

        {   'blur'        : "blur",
            'trans'       : None,
            'blur_fwhm'   : 4,
            'steps'       : [4, 4, 4],
            'tolerance'   : 0.0001,
            'simplex'     : 8 },

        {   'blur'        : "blur",
            'trans'       : None,
            'blur_fwhm'   : 2,
            'steps'       : [2, 2, 2],
            'tolerance'   : 0.0005,
            'simplex'     : 4 }
        ],
        
    'bestlinreg_20171223': [      # re-imelementation from Claude's bestlinreg ~ 2016-12-01
        {   'blur'        : "blur",       # -lsq7 scaling only
            'parameters'  : "-lsq6",
            'trans'       : [ '-est_translations' ],
            'blur_fwhm'   : 8,
            'steps'       : [4, 4, 4],
            'tolerance'   : 0.0001,
            'simplex'     : 16 },

        {   'blur'        : "blur",       # -lsqXX full options
            'parameters'  : "-lsq7",
            'trans'       : None,
            'blur_fwhm'   : 8,
            'steps'       : [4, 4, 4],
            'tolerance'   : 0.0001,
            'simplex'     : 16 },

        {   'blur'        : "blur",
            'trans'       : None,
            'blur_fwhm'   : 4,
            'steps'       : [4, 4, 4],
            'tolerance'   : 0.0001,
            'simplex'     : 8 },

        {   'blur'        : "blur",
            'trans'       : None,
            'blur_fwhm'   : 2,
            'steps'       : [2, 2, 2],
            'tolerance'   : 0.00001,
            'simplex'     : 4,
            'reverse'     : True # replace source and target 
          }
        ]
    }

def linear_register(
    source,
    target,
    output_xfm,
    parameters=None,
    source_mask=None,
    target_mask=None,
    init_xfm=None,
    objective=None,
    conf=None,
    debug=False,
    close=False,
    norot=False,
    noshear=False,
    noshift=False,
    noscale=False,
    work_dir=None,
    start=None,
    downsample=None,
    verbose=0
    ):
    """Perform linear registration, replacement for bestlinreg.pl script
    
    Args:
        source - name of source minc file
        target - name of target minc file
        output_xfm - name of output transformation file
        parameters - registration parameters (optional), can be 
            '-lsq6', '-lsq9', '-lsq12'
        source_mask - name of source mask file (optional)
        target_mask - name of target mask file (optional)
        init_xfm - name of initial transformation file (optional)
        objective - name of objective function (optional), could be 
            '-xcorr' (default), '-nmi','-mi'
        conf - configuration for iterative algorithm (optional) 
               array of dict, or a string describing a flawor
               bestlinreg (default)
               bestlinreg_s
               bestlinreg_s2
               bestlinreg_new - Claude's latest and greatest
        debug - debug flag (optional) , default False
        close - closeness flag (optional) , default False
        norot - disable rotation flag (optional) , default False
        noshear - disable shear flag (optional) , default False
        noshift - disable shift flag (optional) , default False
        noscale - disable scale flag (optional) , default False
        work_dir - working directory (optional) , default create one in temp
        start - initial blurring level, default 16mm from configuration
        downsample - downsample initial files to this step size, default None
        verbose  - verbosity level
    Returns:
        resulting XFM file

    Raises:
        mincError when tool fails
    """
    print("linear_register s:{} s_m:{} t:{} t_m:{} i:{} ".format(source,source_mask,target,target_mask,init_xfm))
    
    with minc_tools.mincTools(verbose=verbose) as minc:
      if not minc.checkfiles(inputs=[source,target], outputs=[output_xfm]):
          return

      # python version
      if conf is None:
          conf = linear_registration_config['bestlinreg']
      elif not isinstance(conf, list): # assume that it is a string
          if conf in linear_registration_config:
            conf = linear_registration_config[conf]
      
      if parameters is None:
          parameters='-lsq9'

      if objective is None:
          objective='-xcorr'
          
      if not isinstance(conf, list): # assume that it is a string
          # assume it's external program's name
          # else run internally
          with minc_tools.mincTools() as m:
              cmd=[conf,source,target,output_xfm]
              if source_mask is not None:
                  cmd.extend(['-source_mask',source_mask])
              if target_mask is not None:
                  cmd.extend(['-target_mask',target_mask])
              if parameters is not None:
                  cmd.append(parameters)
              if objective is not None:
                  cmd.append(objective)
              if init_xfm is not None:
                  cmd.extend(['-init_xfm', init_xfm])
              m.command(cmd, inputs=[source,target], outputs=[output_xfm],verbose=2)
          return output_xfm
      else:

        prev_xfm = None

        s_base=os.path.basename(source).rsplit('.gz',1)[0].rsplit('.mnc',1)[0]
        t_base=os.path.basename(target).rsplit('.gz',1)[0].rsplit('.mnc',1)[0]

        source_lr=source
        target_lr=target
        
        source_mask_lr=source_mask
        target_mask_lr=target_mask
        # figure out what to do here:
        with minc_tools.cache_files(work_dir=work_dir,context='reg') as tmp:
            if downsample is not None:
                source_lr=tmp.cache(s_base+'_'+str(downsample)+'.mnc')
                target_lr=tmp.cache(t_base+'_'+str(downsample)+'.mnc')
                
                minc.resample_smooth(source, source_lr, unistep=downsample)
                minc.resample_smooth(target, target_lr, unistep=downsample)
                
                if source_mask is not None:
                    source_mask_lr=tmp.cache(s_base+'_mask_'+str(downsample)+'.mnc')
                    minc.resample_labels(source_mask,source_mask_lr,unistep=downsample,datatype='byte')
                if target_mask is not None:
                    target_mask_lr=tmp.cache(s_base+'_mask_'+str(downsample)+'.mnc')
                    minc.resample_labels(target_mask,target_mask_lr,unistep=downsample,datatype='byte')
                
            # a fitting we shall go...
            for (i,c) in enumerate(conf):
                _parameters=parameters
                
                if 'parameters' in c and parameters!='-lsq6': # emulate Claude's approach
                    _parameters=c.get('parameters')#'-lsq7'
                
                _reverse = c.get('reverse',False) # swap target and source 
                # set up intermediate files
                if start is not None and start>c['blur_fwhm']:
                    continue
                elif close and c['blur_fwhm']>8:
                    continue
                
                tmp_xfm =    tmp.tmp(s_base+'_'+t_base+'_'+str(i)+'.xfm')

                tmp_source = source_lr
                tmp_target = target_lr

                if c['blur_fwhm']>0: 
                    tmp_source = tmp.cache(s_base+'_'+c['blur']+'_'+str(c['blur_fwhm'])+'.mnc')
                    if not os.path.exists(tmp_source):
                        minc.blur(source_lr,tmp_source,gmag=(c['blur']=='dxyz'), fwhm=c['blur_fwhm'])
                    tmp_target = tmp.cache(t_base+'_'+c['blur']+'_'+str(c['blur_fwhm'])+'.mnc')
                    if not os.path.exists(tmp_target):
                        minc.blur(target_lr,tmp_target,gmag=(c['blur']=='dxyz'), fwhm=c['blur_fwhm'])
                
                if _reverse:
                  args =[  'minctracc', 
                              tmp_target, tmp_source,'-clobber', 
                              _parameters , 
                              objective ,
                          '-simplex', c['simplex'],
                          '-tol',     c['tolerance'] ]
                else:
                  # set up registration
                  args =[  'minctracc', 
                              tmp_source, tmp_target,'-clobber', 
                              _parameters , 
                              objective ,
                          '-simplex', c['simplex'],
                          '-tol',     c['tolerance'] ]

                args.append('-step')
                args.extend(c['steps'])

                # Current transformation at this step
                if prev_xfm is not None:
                    if _reverse :
                      inv_prev_xfm =    tmp.tmp(s_base+'_'+t_base+'_'+str(i)+'_init.xfm')
                      minc.xfminvert(prev_xfm,inv_prev_xfm)
                      args.extend(['-transformation', inv_prev_xfm])
                    else:
                      args.extend(['-transformation', prev_xfm])
                      
                elif init_xfm is not None:
                    # _reverse should not be first?
                    args.extend(['-transformation', init_xfm, '-est_center'])
                elif close:
                    args.append('-identity')
                else:
                    # _reverse should not be first?
                    # Initial transformation will be computed from the from Principal axis 
                    # transformation (PAT).
                    if c['trans'] != '-est_translations':
                        args.append( c['trans'] )
                    else :
                        # will use manual transformation based on shif of CoM, should be identical to '-est_translations' , but it's not
                        com_src=minc.stats(source,['-com','-world_only'],single_value=False)
                        com_trg=minc.stats(target,['-com','-world_only'],single_value=False)
                        diff=[com_trg[k]-com_src[k] for k in range(3)]
                        xfm=tmp.cache(s_base+'_init.xfm')
                        minc.param2xfm(xfm, translation=diff)
                        args.extend( ['-transformation',xfm] )
                
                # masks (even if the blurred image is masked, it's still preferable
                # to use the mask in minctracc)
                if _reverse :
                  if source_mask is not None:
                      args.extend(['-source_mask', source_mask_lr])
                  if target_mask is not None:
                      args.extend(['-model_mask',  target_mask_lr])
                else:
                  if source_mask is not None:
                      args.extend(['-model_mask', source_mask_lr])
                  #disable one mask in this mode
#                  if target_mask is not None:
#                      args.extend(['-source_mask',  target_mask_lr])
                  

                if noshear:
                    args.extend( ['-w_shear',0,0,0] )
                if noscale:
                    args.extend( ['-w_scales',0,0,0] )
                if noshift:
                    args.extend( ['-w_translations',0,0,0] )
                if norot:
                    args.extend( ['-w_rotations',0,0,0] )

                # add files and run registration
                args.append(tmp_xfm)
                minc.command([str(ii) for ii in args],inputs=[tmp_source,tmp_target],outputs=[tmp_xfm])
                
                if _reverse:
                      inv_tmp_xfm =    tmp.tmp(s_base+'_'+t_base+'_'+str(i)+'_sol.xfm')
                      minc.xfminvert(tmp_xfm,inv_tmp_xfm)
                      prev_xfm=inv_tmp_xfm
                else:
                  prev_xfm = tmp_xfm
                
            shutil.copyfile(prev_xfm,output_xfm)
            return output_xfm
      
def linear_register_to_self(
    source,
    target,
    output_xfm,
    parameters=None,
    mask=None,
    target_talxfm=None,
    init_xfm=None,
    model=None,
    modeldir=None,
    close=False,
    nocrop=False,
    noautothreshold=False
    ):
    """perform linear registration, wrapper around mritoself
    
    """

    # TODO convert mritoself to python (?)
    with minc_tools.mincTools() as minc:
        cmd = ['mritoself', source, target, output_xfm]
        if parameters is not None:
            cmd.append(parameters)
        if mask is not None:
            cmd.extend(['-mask', mask])
        if target_talxfm is not None:
            cmd.extend(['-target_talxfm', target_talxfm])
        if init_xfm is not None:
            cmd.extend(['-transform', init_xfm])
        if model is not None:
            cmd.extend(['-model', model])
        if modeldir is not None:
            cmd.extend(['-modeldir', modeldir])
        if close:
            cmd.append('-close')
        if nocrop:
            cmd.append('-nocrop')
        if noautothreshold:
            cmd.append('-noautothreshold')
            cmd.append('-nothreshold')
        minc.command(cmd, inputs=[source, target], outputs=[output_xfm])



def non_linear_register_full(
    source, target, output_xfm, 
    source_mask=None,
    target_mask=None,
    init_xfm=   None,
    level=4,
    start=32,
    parameters=None,
    work_dir=None,
    downsample=None
    ):
    """perform non-linear registration, multiple levels
    Args:
        source - name of source minc file
        target - name of target minc file
        output_xfm - name of output transformation file
        source_mask - name of source mask file (optional)
        target_mask - name of target mask file (optional)
        init_xfm - name of initial transformation file (optional)
        parameters - configuration for iterative algorithm dict (optional)
        work_dir - working directory (optional) , default create one in temp
        start - initial step size, default 32mm 
        level - final step size, default 4mm
        downsample - downsample initial files to this step size, default None

    Returns:
        resulting XFM file

    Raises:
        mincError when tool fails
    """
    with minc_tools.mincTools() as minc:

      if not minc.checkfiles(inputs=[source,target], 
                              outputs=[output_xfm]):
          return

      if parameters is None:
          #print("Using default parameters")
          parameters = {
              'cost':        'corrcoeff',
              'weight':      1,
              'stiffness':   1,
              'similarity':  0.3,
              'sub_lattice': 6,

              'conf': [
                  {'step'        : 32.0,
                  'blur_fwhm'    : 16.0,
                  'iterations'   : 20,
                  'blur'         : 'blur',
                  },
                  {'step'        : 16.0,
                  'blur_fwhm'    : 8.0,
                  'iterations'   : 20,
                  'blur'         : 'blur',
                  },
                  {'step'        : 12.0,
                  'blur_fwhm'    : 6.0,
                  'iterations'   : 20,
                  'blur'         : 'blur',
                  },
                  {'step'        : 8.0,
                  'blur_fwhm'    : 4.0,
                  'iterations'   : 20,
                  'blur'         : 'blur',
                  },
                  {'step'        : 6.0,
                  'blur_fwhm'    : 3.0,
                  'iterations'   : 20,
                  'blur'         : 'blur',
                  },
                  {'step'        : 4.0,
                  'blur_fwhm'    : 2.0,
                  'iterations'   : 10,
                  'blur'         : 'blur',
                  },
                  {'step'        : 2.0,
                  'blur_fwhm'    : 1.0,
                  'iterations'   : 10,
                  'blur'         : 'blur',
                  },
                  {'step'        : 1.0,
                  'blur_fwhm'    : 1.0,
                  'iterations'   : 10,
                  'blur'         : 'blur',
                  },
                  {'step'        : 1.0,
                  'blur_fwhm'    : 0.5,
                  'iterations'   : 10,
                  'blur'         : 'blur',
                  },
                  {'step'        : 0.5,
                  'blur_fwhm'    : 0.25,
                  'iterations'   : 10,
                  'blur'         : 'blur',
                  },
                  ]
              }

      prev_xfm = None
      prev_grid = None

      s_base=os.path.basename(source).rsplit('.gz',1)[0].rsplit('.mnc',1)[0]
      t_base=os.path.basename(target).rsplit('.gz',1)[0].rsplit('.mnc',1)[0]
      
      source_lr=source
      target_lr=target
      
      source_mask_lr=source_mask
      target_mask_lr=target_mask
      
      # figure out what to do here:
      with minc_tools.cache_files(work_dir=work_dir,context='reg') as tmp:
          # a fitting we shall go...
          if downsample is not None:
              source_lr=tmp.cache(s_base+'_'+str(downsample)+'.mnc')
              target_lr=tmp.cache(t_base+'_'+str(downsample)+'.mnc')
              
              minc.resample_smooth(source,source_lr,unistep=downsample)
              minc.resample_smooth(target,target_lr,unistep=downsample)
              
              if source_mask is not None:
                  source_mask_lr=tmp.cache(s_base+'_mask_'+str(downsample)+'.mnc')
                  minc.resample_labels(source_mask,source_mask_lr,unistep=downsample,datatype='byte')
              if target_mask is not None:
                  target_mask_lr=tmp.cache(s_base+'_mask_'+str(downsample)+'.mnc')
                  minc.resample_labels(target_mask,target_mask_lr,unistep=downsample,datatype='byte')
          
          for (i,c) in enumerate(parameters['conf']):

              if   c['step']>start:
                  continue
              elif c['step']<level:
                  break

              # set up intermediate files
              tmp_=        tmp.tmp(s_base+'_'+t_base+'_'+str(i))
              
              tmp_xfm =    tmp_+'.xfm'
              tmp_grid=    tmp_+'_grid_0.mnc'

              tmp_source=source_lr
              tmp_target=target_lr


              if c['blur_fwhm']>0:
                  tmp_source = tmp.cache(s_base+'_'+c['blur']+'_'+str(c['blur_fwhm'])+'.mnc')

                  if not os.path.exists(tmp_source):
                      minc.blur(source_lr,tmp_source,gmag=(c['blur']=='dxyz'),fwhm=c['blur_fwhm'])
                  tmp.unlock(tmp_source)

                  tmp_target = tmp.cache(t_base+'_'+c['blur']+'_'+str(c['blur_fwhm'])+'.mnc')
                  if not os.path.exists(tmp_target):
                      minc.blur(target_lr,tmp_target,gmag=(c['blur']=='dxyz'),fwhm=c['blur_fwhm'])
                  tmp.unlock(tmp_target)

              # set up registration
              args =['minctracc', tmp_source,tmp_target,'-clobber', 
                          '-nonlinear',  parameters['cost'],
                          '-weight',     parameters['weight'],
                          '-stiffness',  parameters['stiffness'],
                          '-similarity', parameters['similarity'],
                          '-sub_lattice',parameters['sub_lattice'],
                      ]

              args.extend(['-iterations',     c['iterations'] ] )
              args.extend(['-lattice_diam',   c['step']*3.0, c['step']*3.0, c['step']*3.0 ] )
              args.extend(['-step',           c['step'],     c['step'],     c['step'] ] )
              
              if c['step']<4:
                  args.append('-no_super')
              
                  # Current transformation at this step
              if prev_xfm is not None:
                  args.extend(['-transformation', prev_xfm])
              elif init_xfm is not None:
                  args.extend(['-transformation', init_xfm])
              else:
                  args.append('-identity')

              # masks (even if the blurred image is masked, it's still preferable
              # to use the mask in minctracc)
              if source_mask is not None:
                  args.extend(['-source_mask',source_mask_lr])
              if target_mask is not None:
                  args.extend(['-model_mask',target_mask_lr])

              # add files and run registration
              args.append(tmp_xfm)

              minc.command([str(ii) for ii in args],
                              inputs=[tmp_source,tmp_target],
                              outputs=[tmp_xfm] )

              prev_xfm  = tmp_xfm
              prev_grid = tmp_grid

          # done
          if prev_xfm is None:
              raise minc_tools.mincError("No iterations were performed!")

          # STOP-gap measure to save space for now
          # TODO: fix minctracc?
          # TODO: fix mincreshape too!
          minc.calc([prev_grid],'A[0]',tmp.tmp('final_grid_0.mnc'),datatype='-float')
          shutil.move(tmp.tmp('final_grid_0.mnc'),prev_grid)
            
          minc.param2xfm(tmp.tmp('identity.xfm'))
          minc.xfmconcat([tmp.tmp('identity.xfm'),prev_xfm],output_xfm)
          return output_xfm

def non_linear_register_increment(
    source,
    target,
    output_xfm,
    source_mask=None,
    target_mask=None,
    init_xfm=None,
    level=4,
    parameters=None,
    work_dir=None,
    downsample=None
    ):
    """perform non-linear registration, increment right now there are no 
    difference with non_linear_register_full , 
    with start and level set to same value
    Args:
        source - name of source minc file
        target - name of target minc file
        output_xfm - name of output transformation file
        source_mask - name of source mask file (optional)
        target_mask - name of target mask file (optional)
        init_xfm - name of initial transformation file (optional)
        parameters - configuration for iterative algorithm dict (optional)
        work_dir - working directory (optional) , default create one in temp
        level - final step size, default 4mm
        downsample - downsample initial files to this step size, default None

    Returns:
        resulting XFM file

    Raises:
        mincError when tool fails
    """
    
    return non_linear_register_full(source,target,output_xfm,
          source_mask=source_mask,
          target_mask=target_mask,
          init_xfm=init_xfm,
          level=level,
          start=level,
          parameters=parameters,
          work_dir=work_dir,
          downsample=downsample)



def parse_options():
    parser = argparse.ArgumentParser(
                    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                    description="Run minctracc-based registration")
    
    parser.add_argument("--verbose",
                    action="store_true",
                    default=False,
                    help="Be verbose",
                    dest="verbose")
                    
    parser.add_argument("source",
                    help="Source file")
    
    parser.add_argument("target",
                    help="Target file")
    
    parser.add_argument("output_xfm",
                    help="Output transformation file, xfm format")
    
    parser.add_argument("--source_mask",
                        default= None,
                        help="Source mask")
    
    parser.add_argument("--target_mask",
                        default= None,
                        help="Target mask")
    
    parser.add_argument("--init_xfm",
                        default   = None,
                        help="Initial transformation, minc format")
    
    parser.add_argument("--work_dir",
                        default   = None,
                        help="Work directory")
    
    parser.add_argument("--downsample",
                        default = None,
                        help="Downsample to given voxel size ",
                        type=float)

    parser.add_argument("--start",
                        default = None,
                        help="Start level of registration 32 for nonlinear, 16 for linear",
                        type=float)
    
    parser.add_argument("--level",
                        default = 4.0,
                        help="Final level of registration (nl)",
                        type=float)
    
    parser.add_argument("--nl",
                    action="store_true",
                    dest='nl',
                    help="Use nonlinear mode",
                    default=False)
    
    parser.add_argument("--lin",
                    help="Linear mode, default lsq6",
                    default='lsq6')
    
    parser.add_argument("--objective",
                    default="xcorr",
                    help="Registration objective function (linear)")
    
    parser.add_argument("--conf",
                    default="bestlinreg_s2",
                    help="Linear registrtion configuration")
    

    options = parser.parse_args()
    return options


if __name__ == "__main__":
    options = parse_options()

    if options.source is None or options.target is None:
         print("Error in arguments, run with --help")
         print(repr(options))
    else:
        
        if options.nl :
            if options.start is None:
                options.start=32.0
            
            non_linear_register_full( 
                        options.source, options.target, options.output_xfm,
                        source_mask= options.source_mask,
                        target_mask= options.target_mask,
                        init_xfm   = options.init_xfm,
                        start      = options.start,
                        level      = options.level,
                        work_dir   = options.work_dir,
                        downsample = options.downsample)
        else:
            if options.start is None:
                options.start=16.0
            _verbose=0
            if options.verbose: _verbose=2
            
            linear_register(
                        options.source, options.target, options.output_xfm,
                        source_mask= options.source_mask,
                        target_mask= options.target_mask,
                        init_xfm   = options.init_xfm,
                        #start      = options.start,
                        work_dir   = options.work_dir,
                        downsample = options.downsample,
                        objective  = '-'+options.objective,
                        conf       = options.conf,
                        parameters = '-'+options.lin,
                        verbose    = _verbose
                        )
            
# kate: space-indent on; indent-width 4; indent-mode python;replace-tabs on;word-wrap-column 80
