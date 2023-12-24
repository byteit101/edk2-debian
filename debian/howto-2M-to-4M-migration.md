# How to migrate from 2M to 4M firmware images #

## VMs using separate CODE/VARS pflash images ##

  1. Shutdown your VM.
  1. Locate the separate CODE and VARS pflash images used by your
     VM. VMs typically use the CODE images installed by `ovmf`
     directly because they are read-only and can be shared. However,
     each VM should have its own VARS image copy that it can write
     to. Note: For libvirt-based VMs, these paths can be found in the
     `<os>` element of the domain XML for the VM. The `<loader>`
     sub-element points to the CODE image and the `<nvram>`
     sub-element points to the VARS image.
  1. Replace the 2M CODE image path with the counterpart 4M CODE image path:

     | 2M                                     | 4M                                        |
     |----------------------------------------|-------------------------------------------|
     | `/usr/share/OVMF/OVMF_CODE.fd`         | `/usr/share/OVMF/OVMF_CODE_4M.fd`         |
     | `/usr/share/OVMF/OVMF_CODE.ms.fd`      | `/usr/share/OVMF/OVMF_CODE_4M.ms.fd`      |
     | `/usr/share/OVMF/OVMF_CODE.secboot.fd` | `/usr/share/OVMF/OVMF_CODE_4M.secboot.fd` |

  1. Use the `virt-fw-vars` utility from the `python3-virt-firmware`
     package to dump the variable contents from the existing VARS
     image, replace it with a new 4M image, and restore the saved
     variable contents. A sample script is provided:

   ```
      # apt install -y python3-virt-firmware  
      # bash /usr/share/doc/ovmf/2M_VARS-to-4M_VARS.sh -i vm_VARS.fd  
      Backing up vm_VARS.fd to vm_VARS.fd.1703354741  
      INFO: reading raw edk2 varstore from vm_VARS.fd  
      INFO: var store range: 0x64 -> 0x40000  
      INFO: writing json varstore to /tmp/tmp.bP2jFSFVG8  
      INFO: reading raw edk2 varstore from /usr/share/OVMF/OVMF_VARS_4M.fd  
      INFO: var store range: 0x64 -> 0x40000  
      INFO: set variable 525400CD1990 from /tmp/tmp.bP2jFSFVG8  
      [...]  
      INFO: set variable certdb from /tmp/tmp.bP2jFSFVG8  
      INFO: set variable db from /tmp/tmp.bP2jFSFVG8  
      INFO: set variable dbx from /tmp/tmp.bP2jFSFVG8  
      INFO: writing raw edk2 varstore to vm_VARS.fd  
   ```

  1. You can now safely restart your VM. Once you have verified that
     the conversion process was successful, you may consider removing
     the backup file.

## VMs using a unified CODE/VARS image ##

If you have VMs using a copy of a 2M unified image, then those VMs are
already divorced and are unaffected by the removal of the unified
image from `ovmf`. You should consider migrating these to separate
CODE/VARS pflash images if you wish to benefit from `ovmf` package
updates, but it is not required.

### Migrating VMs using unified CODE/VARS image to separate CODE/VARS pflash images ###

QEMU's `-bios` option is used to boot a unified CODE/VARS image. You will need
to replace this option with separate `-pflash` options that point to individual
CODE and VARS files.

1. `/usr/share/OVMF/OVMF_CODE_4M.fd` is the functional equivalent of
   the CODE section in the unified image. If you wish to review the other
   CODE options, consult `/usr/share/doc/ovmf/README.Debian`. CODE images
   require only read access, so VMs can share the system copy.

1. You will now need to create a separate VARS file for each VM.

    * If you were using `/usr/share/ovmf/OVMF.fd` or
      `/usr/share/qemu/OVMF.fd` directly, you presumably were not
      using persistent variable storage, and can start with an empty
      variable store template. `/usr/share/OVMF/OVMF_VARS_4M.fd` is
      the functional equivalent of the VARS section in the previously
      provided unified image. If you wish to review the other VARS
      options, consult `/usr/share/doc/ovmf/README.Debian`.

    * If your VM(s) used a divorced copy of a unified image, you can
      use the `virt-fw-vars` utility from the `python3-virt-firmware`
      package to initialize a new VARS image with the variables from
      the existing unified image. A sample script is provided:

   ```
      # apt install -y python3-virt-firmware  
      # bash /usr/share/doc/ovmf/2M_VARS-to-4M_VARS.sh -i OVMF.fd -o vm_VARS.fd  
      INFO: reading raw edk2 varstore from OVMF.fd  
      INFO: var store range: 0x64 -> 0x40000  
      INFO: writing json varstore to /tmp/tmp.huJ5wEmlTM  
      INFO: reading raw edk2 varstore from /usr/share/OVMF/OVMF_VARS_4M.fd  
      INFO: var store range: 0x64 -> 0x40000  
      INFO: writing raw edk2 varstore to vm_VARS.fd  
   ```

1. Replace the `-bios` option with separate `pflash` options:

   ```
   qemu-system-x86_64 -bios OVMF.fd  
   ```

   becomes:

   ```
   qemu-system-x86_64 \  
     -drive if=pflash,format=raw,unit=0,readonly=on,file=/usr/share/OVMF/OVMF_CODE_4M.fd \  
     -drive if=pflash,format=raw,unit=1,readonly=off,file=vm_VARS.fd
   ```
