#!/usr/bin/python3
# coding=utf-8

import argparse
import datetime
import sys
import time

import torch
import torch.nn.functional as F

# from apex import amp
from tensorboardX import SummaryWriter
from torch.utils.data import DataLoader

import dataset
from dataset import Data
from net import F3Net

sys.path.insert(0, "../")
sys.dont_write_bytecode = True


def parse_args():
    parser = argparse.ArgumentParser(description="Train Pipeline F3-Net")
    parser.add_argument(
        "--data", type=str, default="../data/DUTS", help="Path to train dataset"
    )
    parser.add_argument(
        "--out", type=str, default="./out", help="Path where outputs will be stored"
    )
    parser.add_argument(
        "--epochs", type=int, default=32, help="Path where outputs will be stored"
    )
    args = parser.parse_args()
    return args


def structure_loss(pred, mask):
    weit = 1 + 5 * torch.abs(
        F.avg_pool2d(mask, kernel_size=31, stride=1, padding=15) - mask
    )
    wbce = F.binary_cross_entropy_with_logits(pred, mask, reduce="none")
    wbce = (weit * wbce).sum(dim=(2, 3)) / weit.sum(dim=(2, 3))

    pred = torch.sigmoid(pred)
    inter = ((pred * mask) * weit).sum(dim=(2, 3))
    union = ((pred + mask) * weit).sum(dim=(2, 3))
    wiou = 1 - (inter + 1) / (union - inter + 1)
    return (wbce + wiou).mean()


def train(Dataset, Network, args):
    # dataset
    cfg = Dataset.Config(
        datapath=args.data,
        savepath=args.out,
        mode="train",
        batch=32,
        lr=0.05,
        momen=0.9,
        decay=5e-4,
        epoch=args.epochs,
    )
    data = Dataset.Data(cfg)
    loader = DataLoader(
        data, collate_fn=Data.collate, batch_size=cfg.batch, shuffle=True, num_workers=8
    )
    # network
    net = Network(cfg)
    net.train(True)
    net.cuda()
    # parameter
    base, head = [], []
    for name, param in net.named_parameters():
        if "bkbone.conv1" in name or "bkbone.bn1" in name:
            print(name)
        elif "bkbone" in name:
            base.append(param)
        else:
            head.append(param)
    optimizer = torch.optim.SGD(
        [{"params": base}, {"params": head}],
        lr=cfg.lr,
        momentum=cfg.momen,
        weight_decay=cfg.decay,
        nesterov=True,
    )
    # Apex AMP
    # net, optimizer = amp.initialize(net, optimizer, opt_level="O2")

    # Torch AMP
    scaler = torch.cuda.amp.GradScaler()

    sw = SummaryWriter(cfg.savepath)
    global_step = 0

    for epoch in range(cfg.epoch):
        optimizer.param_groups[0]["lr"] = (
            (1 - abs((epoch + 1) / (cfg.epoch + 1) * 2 - 1)) * cfg.lr * 0.1
        )
        optimizer.param_groups[1]["lr"] = (
            1 - abs((epoch + 1) / (cfg.epoch + 1) * 2 - 1)
        ) * cfg.lr

        for step, (image, mask) in enumerate(loader):
            image, mask = image.cuda().float(), mask.cuda().float()
            with torch.cuda.amp.autocast():
                out1u, out2u, out2r, out3r, out4r, out5r = net(image)

                loss1u = structure_loss(out1u, mask)
                loss2u = structure_loss(out2u, mask)

                loss2r = structure_loss(out2r, mask)
                loss3r = structure_loss(out3r, mask)
                loss4r = structure_loss(out4r, mask)
                loss5r = structure_loss(out5r, mask)
                loss = (
                    (loss1u + loss2u) / 2
                    + loss2r / 2
                    + loss3r / 4
                    + loss4r / 8
                    + loss5r / 16
                )

            # Apex AMP
            # optimizer.zero_grad()
            # with amp.scale_loss(loss, optimizer) as scale_loss:
            #     scale_loss.backward()
            # optimizer.step()

            # Torch AMP
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()

            # log
            global_step += 1
            sw.add_scalar(
                "lr", optimizer.param_groups[0]["lr"], global_step=global_step
            )
            sw.add_scalars(
                "loss",
                {
                    "loss1u": loss1u.item(),
                    "loss2u": loss2u.item(),
                    "loss2r": loss2r.item(),
                    "loss3r": loss3r.item(),
                    "loss4r": loss4r.item(),
                    "loss5r": loss5r.item(),
                },
                global_step=global_step,
            )
            if step % 10 == 0:
                print(
                    "%s | step:%d/%d/%d | lr=%.6f | loss=%.6f"
                    % (
                        datetime.datetime.now(),
                        global_step,
                        epoch + 1,
                        cfg.epoch,
                        optimizer.param_groups[0]["lr"],
                        loss.item(),
                    )
                )

        if epoch > cfg.epoch / 3 * 2:
            torch.save(net.state_dict(), cfg.savepath + "/model-" + str(epoch + 1))
            print(f"Model saved at: {cfg.savepath + '/model-' + str(epoch + 1)}")


if __name__ == "__main__":
    parsed_args = parse_args()
    startTime = time.time()
    train(dataset, F3Net, parsed_args)
    print("The script took {0} seconds !".format(time.time() - startTime))
    # print
    # print
