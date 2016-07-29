#!/usr/bin/env python
# encoding: utf-8
from sole_models.statistics.china_mobile import get_cb_infos
from sole_models.statistics.china_union import get_um_info
from sole_models.sole_orm import china_unicom_orm_desplay,china_mobile_orm_desplay
def test():
    token_list=[
        '60e2eef6-4400-11e6-9fed-00163e106b48',
        'f459f41c-4401-11e6-8d41-00163e106b48',
        'b67885d2-4406-11e6-aeea-00163e106b48',
        'fa4663ce-4424-11e6-a8c6-00163e106b48',
        '2e268c32-4425-11e6-b9c3-00163e106b48',
        '92e13368-4428-11e6-86af-00163e106b48',
        '84b20a82-44b5-11e6-aa2e-00163e106b48',
        '2b0f4d62-44b7-11e6-ab21-00163e106b48',
        '8cdfba38-44d8-11e6-aa2e-00163e106b48',
        '667aa09c-44f6-11e6-9fc1-00163e106b48',
        '83f9e20a-450e-11e6-9798-00163e106b48',
        'bd3075f8-4517-11e6-af10-00163e106b48',
        '5033695e-4519-11e6-9798-00163e106b48',
        '2abc220e-452a-11e6-8582-00163e106b48',
        'c114fc9a-453d-11e6-a272-00163e106b48',
        '85da6b2e-4542-11e6-8582-00163e106b48',
        '7f72a6e6-4571-11e6-9798-00163e106b48',
        'bf40143a-4575-11e6-a272-00163e106b48',
        'eb906b60-4576-11e6-9798-00163e106b48',
        'fb46bdfe-4579-11e6-8582-00163e106b48',
        '88926b40-457f-11e6-9798-00163e106b48',
        '633b47e8-4581-11e6-9798-00163e106b48',
        'eaacfa2c-4582-11e6-9798-00163e106b48',
        '9920bf08-4583-11e6-9798-00163e106b48',
        'e9d9fd7e-459c-11e6-9798-00163e106b48',
        'ba057e56-45a7-11e6-8582-00163e106b48',
        'b8e784f6-45a7-11e6-af10-00163e106b48',
        'df0d0686-45b3-11e6-8eb4-00163e106b48',
        'fbb0e666-45ba-11e6-8eb4-00163e106b48',
        '3c046a3a-4665-11e6-ae0b-00163e106b48',
        'cd358e92-4667-11e6-ae0b-00163e106b48',
        '68316d8e-4669-11e6-ae0b-00163e106b48',
        '20682f32-4697-11e6-ac12-00163e106b48',
        '83ea5516-4715-11e6-9f9c-00163e106b48',
        'fae680e0-4715-11e6-ae0b-00163e106b48',
        '74f4ce58-4718-11e6-95b6-00163e106b48',
        'f827f8b4-4726-11e6-ae0b-00163e106b48',
        'c396adce-4727-11e6-ac12-00163e106b48',
        '3943f07a-472a-11e6-ae0b-00163e106b48',
        'db4e5d12-4728-11e6-ae0b-00163e106b48',
        '1e033a3c-472f-11e6-ac12-00163e106b48',
        '93ac0a14-4736-11e6-9470-00163e106b48',
        '06557168-4737-11e6-958c-00163e106b48',
        '2a9ff2f4-4738-11e6-958c-00163e106b48',
        '36449fca-473c-11e6-958c-00163e106b48',
        'c4fd9890-477b-11e6-9a34-00163e106b48',
        'c9414884-480c-11e6-b454-00163e106b48',
        'f3f64242-481a-11e6-9a34-00163e106b48',
        'd64c9860-4822-11e6-9a34-00163e106b48',
        '6debcb08-4839-11e6-b454-00163e106b48',
        'a1efb4f2-483c-11e6-9a34-00163e106b48',
        '72992084-483d-11e6-9a34-00163e106b48',
        '775aed72-48bb-11e6-b209-00163e106b48',
        '1359a7ca-48be-11e6-b454-00163e106b48',
        'd964053a-48c0-11e6-b209-00163e106b48',
        '8226690a-48c2-11e6-9a34-00163e106b48',
        '6705e272-48c2-11e6-9a34-00163e106b48',
        '8d6779ec-48c9-11e6-9a34-00163e106b48',
        '8a920f1c-48dc-11e6-b757-00163e106b48',
        'e1bfaac8-48dd-11e6-b454-00163e106b48',
        '712756e4-4969-11e6-b454-00163e106b48',
        '8c2685d4-4999-11e6-9a34-00163e106b48',
        '2b58e798-499d-11e6-9a34-00163e106b48',
        '44bd807a-499f-11e6-ab9b-00505624729e',
        '8f56b70a-49b8-11e6-b454-00163e106b48',
        'f225c94c-49b9-11e6-b454-00163e106b48',
        '35dccb72-49ba-11e6-b454-00163e106b48',
        '2f69a25e-49bc-11e6-b454-00163e106b48',
        '03597dc8-49bd-11e6-b454-00163e106b48',
        '07d49b0c-49be-11e6-b454-00163e106b48',
        '2128b0ce-49bf-11e6-b454-00163e106b48',
        '453908be-49c0-11e6-b454-00163e106b48',
        'f3100dd4-49c0-11e6-b454-00163e106b48',
        'acbb612a-49c1-11e6-b454-00163e106b48',
        '7d4d0abe-49c2-11e6-b454-00163e106b48',
        '327b7678-49c3-11e6-b454-00163e106b48',
        'd35c489c-49d7-11e6-9ae6-00163e106b48',
        'e9cb2b9c-49e2-11e6-9da0-00163e106b48',
        '6144962a-4a53-11e6-9e6c-00163e106b48',
        '5eb07228-4a88-11e6-8442-00163e106b48',
        '04b9be86-4b01-11e6-8442-00163e106b48',
        'c9d4fd9a-4b31-11e6-84ab-00163e106b48',
        'b8b3fcb8-4b64-11e6-8442-00163e106b48',
        '31abd3cc-4bc7-11e6-84ab-00163e106b48',
        'cb69303a-4bc8-11e6-84ab-00163e106b48',
        '61c4a54c-4bcd-11e6-84ab-00163e106b48',
        'ad80f110-4bce-11e6-84ab-00163e106b48',
        'e37381ec-4bcf-11e6-84ab-00163e106b48',
        'a5effb56-4bd0-11e6-84ab-00163e106b48',
        '62c38bd0-4bd1-11e6-86b1-00163e106b48',
        'b855a5c8-4bd2-11e6-84ab-00163e106b48',
        'b07a45d6-4bda-11e6-84ab-00163e106b48',
        '5e3f6408-4bdb-11e6-84ab-00163e106b48',
        '9854a016-4bdd-11e6-84ab-00163e106b48',
        '829649a4-4bde-11e6-84ab-00163e106b48',
        'adfcaf74-4bdf-11e6-8442-00163e106b48',
        '5b79063e-4be0-11e6-86b1-00163e106b48',
        '542dab9a-4be1-11e6-84ab-00163e106b48',
        'e77ff204-4be1-11e6-84ab-00163e106b48',
        '8a0872f8-4be2-11e6-84ab-00163e106b48',
        '1f10c166-4be3-11e6-86b1-00163e106b48',
        '4cdaeb16-4be4-11e6-86b1-00163e106b48',
        '6ee53cbe-4be6-11e6-80f0-00163e106b48',
        '007a4ba4-4be9-11e6-84ab-00163e106b48',
        '5e6427c6-4bee-11e6-80f0-00163e106b48',
        '20e7bce4-4bf0-11e6-84ab-00163e106b48',
        '7a8d2702-4bf5-11e6-84ab-00163e106b48',
        'ed23e61a-4c1e-11e6-86b1-00163e106b48',
        'd763472e-4c61-11e6-86b1-00163e106b48',
        '00e16eba-4ce8-11e6-b818-00163e106b48',
        '906aa92e-4ce9-11e6-b818-00163e106b48',
        '4af3600a-4ceb-11e6-b818-00163e106b48',
        'bf391792-4cec-11e6-832a-00163e106b48',
        '8784769c-4ced-11e6-b818-00163e106b48',
        '3d4fe6a0-4cee-11e6-b818-00163e106b48',
        '9e726144-4cf6-11e6-b84f-00163e106b48',
        '55640448-4cf7-11e6-b84f-00163e106b48',
        '7aa710e6-4cfd-11e6-b84f-00163e106b48',
        '25ee57f2-4cfe-11e6-b84f-00163e106b48',
        '9608c0fc-4d55-11e6-b84f-00163e106b48',
        'b3a32188-4d5b-11e6-822c-00163e106b48',
        'a5da50a2-4d75-11e6-a19a-00163e162482',
        '6444ae84-4da8-11e6-a6f3-00163e162482',
        '2f93433e-4dae-11e6-8735-00163e162482',
        '25654280-4e18-11e6-8735-00163e162482',
        '05618b08-4e25-11e6-8735-00163e162482',
         'e49ff0c4-4e26-11e6-9b68-00163e106b48',
        # '6cf358d0-43f5-11e6-9fed-00163e106b48',
        # 'a194f932-442b-11e6-83b8-00163e106b48',
        # '19dcee76-442d-11e6-83b8-00163e106b48',
        # '586e78f2-442e-11e6-83b8-00163e106b48',
        # 'fc0fda22-442f-11e6-83b8-00163e106b48',
        # '7f302a7a-444d-11e6-ab21-00163e106b48',
        # '114ef27a-4452-11e6-ab21-00163e106b48',
        # '63dd29a2-4453-11e6-ab21-00163e106b48',
        # 'e496fa5a-4453-11e6-ab21-00163e106b48',
        # '4ed247f6-44b0-11e6-84d5-00163e106b48',
        # '041bad66-44cd-11e6-ab21-00163e106b48',
        # '5037e282-44dc-11e6-ab21-00163e106b48',
        # 'e880e48e-44e7-11e6-b974-00163e106b48',
        # '54bf105e-44ec-11e6-ab21-00163e106b48',
        # '31e3d3b2-4500-11e6-8582-00163e106b48',
        # '9cac8604-4572-11e6-8582-00163e106b48',
        # '700cd5a8-4578-11e6-a272-00163e106b48',
        # '4fa961aa-4582-11e6-9798-00163e106b48',
        # 'c7c77794-45af-11e6-a604-00163e106b48',
        # '7e0cbbbe-45b4-11e6-a0a9-00163e106b48',
        # '9db14b24-45be-11e6-8eb4-00163e106b48',
        # 'edc4db86-45db-11e6-ac12-00163e106b48',
        # '9aefd2ce-4628-11e6-9f9c-00163e106b48',
        # '7d51664e-464e-11e6-ac12-00163e106b48',
        # 'fd70b8a2-46a8-11e6-9f9c-00163e106b48',
        # '843d4446-472a-11e6-95b6-00163e106b48',
        # '43074a24-4731-11e6-ae0b-00163e106b48',
        # '29029d8a-474b-11e6-958c-00163e106b48',
        # 'f65f4ada-475f-11e6-9a34-00163e106b48',
        # 'a892bad6-4763-11e6-9a34-00163e106b48',
        # 'b3ec19c0-4765-11e6-9a34-00163e106b48',
        # 'ea5f0f7e-476c-11e6-9a34-00163e106b48',
        # 'cac47db6-4780-11e6-9a34-00163e106b48',
        # '50d211b6-47cc-11e6-9a34-00163e106b48',
        # '1b1bcc60-47d6-11e6-9a34-00163e106b48',
        # '0648edb4-47ee-11e6-b757-00163e106b48',
        # 'd986b274-47ee-11e6-9a34-00163e106b48',
        # 'a1df6392-4803-11e6-9a34-00163e106b48',
        # '8f09272a-4809-11e6-b454-00163e106b48',
        # '0fd976b2-4818-11e6-b757-00163e106b48',
        # '7039f1f4-4830-11e6-9a34-00163e106b48',
        # '0bc3cbe4-48e1-11e6-9a34-00163e106b48',
        # 'b62b6200-4958-11e6-b757-00163e106b48',
        # 'ae904b66-4979-11e6-9a34-00163e106b48',
        # '238bb62c-4997-11e6-9a34-00163e106b48',
        # 'f61a1202-499f-11e6-9a34-00163e106b48',
        # '6a072b26-49cf-11e6-b454-00163e106b48',
        # 'a3b067cc-4a13-11e6-b6cf-00163e106b48',
        # '6a072b26-49cf-11e6-b454-00163e106b48',
        # '5f22b282-4a35-11e6-9e6c-00163e106b48',
        # '04d1e5d0-4a46-11e6-9e6c-00163e106b48',
        # '913033f8-4a53-11e6-9e6c-00163e106b48',
        # 'f8ef4968-4a7e-11e6-84ab-00163e106b48',
        # 'bdf68eae-4a81-11e6-80f0-00163e106b48',
        # '7f88664a-4a9c-11e6-84ab-00163e106b48',
        # 'b8b3e09a-4af9-11e6-84ab-00163e106b48',
        # '467c1af4-4afb-11e6-80f0-00163e106b48',
        # '11143354-4b20-11e6-84ab-00163e106b48',
        # 'e6fffa30-4b1f-11e6-84ab-00163e106b48',
        # '30641980-4b2b-11e6-86b1-00163e106b48',
        # 'a54ff578-4b37-11e6-86b1-00163e106b48',
        # '02e4039e-4b67-11e6-86b1-00163e106b48',
        # '1bc78cd4-4c19-11e6-86b1-00163e106b48',
        # '15a74546-4c2e-11e6-80f0-00163e106b48',
        # '49e29592-4cb3-11e6-b818-00163e106b48',
        # '920a9f6c-4ceb-11e6-b818-00163e106b48',
        # '1ecb0134-4d6a-11e6-bae1-00163e162482',
        # 'b70d9486-4d68-11e6-bae1-00163e162482',
        # 'fe034f28-4d79-11e6-a6f3-00163e162482',
        # 'ec288988-4d7b-11e6-a19a-00163e162482',
        # '5192939e-4d7d-11e6-a6f3-00163e162482',
        # '9d9034d0-4d83-11e6-a6f3-00163e162482',
        # '1a9329ce-4d84-11e6-a6f3-00163e162482',
        # 'c8ef0482-4dc7-11e6-8735-00163e162482',      

    ]
    for it in token_list:
        print it
        cnd={'token':it}
        cc=china_unicom_orm_desplay(cnd)
        print get_um_info(cc)





    