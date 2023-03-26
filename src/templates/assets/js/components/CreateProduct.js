import React, {useState} from 'react';
import TagsInput from 'react-tagsinput';
import 'react-tagsinput/react-tagsinput.css';
import Dropzone from 'react-dropzone'
import axios from 'axios';


const CreateProduct = (props) => {

    const [productVariantPrices, setProductVariantPrices] = useState([])

    const [productImageData, setProductImageData] = useState([])
    const [imagePathData, setimagePathData] = useState([])
    const [productDetailsData, setProductDetailsData] = useState({})

    const onProductDetailDataChange = (event) => {
        const {name, value} = event.target;
        setProductDetailsData(prevS => {
            return {
                ...prevS,
                [name]: value
            }
        })
    }
    const [productVariants, setProductVariant] = useState([
        {
            option: 1,
            tags: []
        }
    ])
    // handle click event of the Add button
    const handleAddClick = () => {
        let all_variants = JSON.parse(props.variants.replaceAll("'", '"')).map(el => el.id)
        let selected_variants = productVariants.map(el => el.option);
        let available_variants = all_variants.filter(entry1 => !selected_variants.some(entry2 => entry1 == entry2))
        setProductVariant([...productVariants, {
            option: available_variants[0],
            tags: []
        }])
    };

    // handle input change on tag input
    const handleInputTagOnChange = (value, index) => {
        let product_variants = [...productVariants]
        product_variants[index].tags = value
        setProductVariant(product_variants)

        checkVariant()
    }

    // remove product variant
    const removeProductVariant = (index) => {
        let product_variants = [...productVariants]
        product_variants.splice(index, 1)
        setProductVariant(product_variants)
    }

    // check the variant and render all the combination
    const checkVariant = () => {
        let tags = [];

        productVariants.filter((item) => {
            tags.push(item.tags)
        })
        console.log('tags = ', tags);

        setProductVariantPrices([])

        getCombn(tags).forEach(item => {
            setProductVariantPrices(productVariantPrice => [...productVariantPrice, {
                title: item,
                price: 0,
                stock: 0
            }])
        })

    }

    // combination algorithm
    function getCombn(arr, pre) {
        pre = pre || '';
        if (!arr.length) {
            return pre;
        }
        let ans = arr[0].reduce(function (ans, value) {
            return ans.concat(getCombn(arr.slice(1), pre + value + '/'));
        }, []);
        return ans;
    }

    // product variant price and stock change
    const onProductVariantPriceAndStockChange = (event, productVariantTitle ) =>{
        const {name, value} = event.target;

        setProductVariantPrices(prevS => {
            return prevS.map(i => i.title === productVariantTitle ? {...i, [name]: value} : i)
        })
    }

    // const ProductImageUpload = (acceptedFiles) =>{
    //     let images = [];
    //     let imagePath = [];
    //     for (let i=0; i<acceptedFiles.length; i++){
    //         images.push(acceptedFiles[i])
    //         imagePath.push(acceptedFiles[i].path)
    //     }
    //     console.log('access data = ', images);
    //     setProductImageData(images)
    //     setimagePathData(imagePath)
    // }

    



    // Save product
    let saveProduct = (event) => {
        event.preventDefault();
        // TODO : write your code here to save the product
        console.log('productImageData = ', productImageData);
        console.log('productDetailsData = ', productDetailsData);
        console.log('productVariantPrices = ', productVariantPrices);
        console.log('productVariants = ', productVariants);
        let formData = new FormData();

        formData.append("product_details", JSON.stringify(productDetailsData));
        productImageData && formData.append("product_image", productImageData[0]);
        formData.append("product_variants", JSON.stringify(productVariants));
        formData.append("product_variant_prices", JSON.stringify(productVariantPrices));

        console.log('formdata = ', formData);
        axios({
            url: '/product/api/create-product/',
            method: "post",
            data: formData,
            headers: {
                "Content-Type": "multipart/form-data",
            },
        })
        .then(res => {
            
            window.location.href = "/product/list/"
        })
        .catch(err => {
            console.log('e = ', err);
            
                alert(err.message)
            
        })

    }


    return (
        <div>
            <section>
                <div className="row">
                    <div className="col-md-6">
                        <div className="card shadow mb-4">
                            <div className="card-body">
                                <div className="form-group">
                                    <label htmlFor="">Product Name</label>
                                    <input type="text" name='title' id='title' value={productDetailsData.title} onChange={onProductDetailDataChange} placeholder="Product Name" className="form-control"/>
                                </div>
                                <div className="form-group">
                                    <label htmlFor="">Product SKU</label>
                                    <input type="text" name='sku' id='sku' value={productDetailsData.sku} onChange={onProductDetailDataChange} placeholder="Product SKU" className="form-control"/>
                                </div>
                                <div className="form-group">
                                    <label htmlFor="">Description</label>
                                    <textarea id="description" name='description' cols="30" rows="4" value={productDetailsData.description} onChange={onProductDetailDataChange} className="form-control"></textarea>
                                </div>
                            </div>
                        </div>

                        <div className="card shadow mb-4">
                            <div
                                className="card-header py-3 d-flex flex-row align-items-center justify-content-between">
                                <h6 className="m-0 font-weight-bold text-primary">Media</h6>
                            </div>
                            <div className="card-body border">
                            
                            <Dropzone onDrop={acceptedFiles => setProductImageData(acceptedFiles)}>
                                    {({getRootProps, getInputProps}) => (
                                        <section>
                                            <div {...getRootProps()}>
                                                <input {...getInputProps()} />
                                                <p>Drag 'n' drop some files here, or click to select files</p>
                                            </div>
                                        </section>
                                    )}
                                </Dropzone>
                                
                            </div>
                            
                        </div>
                    </div>

                    <div className="col-md-6">
                        <div className="card shadow mb-4">
                            <div
                                className="card-header py-3 d-flex flex-row align-items-center justify-content-between">
                                <h6 className="m-0 font-weight-bold text-primary">Variants</h6>
                            </div>
                            <div className="card-body">

                                {
                                    productVariants.map((element, index) => {
                                        return (
                                            <div className="row" key={index}>
                                                <div className="col-md-4">
                                                    <div className="form-group">
                                                        <label htmlFor="">Option</label>
                                                        <select className="form-control" defaultValue={element.option}>
                                                            {
                                                                JSON.parse(props.variants.replaceAll("'", '"')).map((variant, index) => {
                                                                    return (<option key={index}
                                                                                    value={variant.id}>{variant.title}</option>)
                                                                })
                                                            }

                                                        </select>
                                                    </div>
                                                </div>

                                                <div className="col-md-8">
                                                    <div className="form-group">
                                                        {
                                                            productVariants.length > 1
                                                                ? <label htmlFor="" className="float-right text-primary"
                                                                         style={{marginTop: "-30px"}}
                                                                         onClick={() => removeProductVariant(index)}>remove</label>
                                                                : ''
                                                        }

                                                        <section style={{marginTop: "30px"}}>
                                                            <TagsInput value={element.tags}
                                                                       style="margin-top:30px"
                                                                       onChange={(value) => handleInputTagOnChange(value, index)}/>
                                                        </section>

                                                    </div>
                                                </div>
                                            </div>
                                        )
                                    })
                                }


                            </div>
                            <div className="card-footer">
                                {productVariants.length !== 3
                                    ? <button className="btn btn-primary" onClick={handleAddClick}>Add another
                                        option</button>
                                    : ''
                                }

                            </div>

                            <div className="card-header text-uppercase">Preview</div>
                            <div className="card-body">
                                <div className="table-responsive">
                                    <table className="table">
                                        <thead>
                                        <tr>
                                            <td>Variant</td>
                                            <td>Price</td>
                                            <td>Stock</td>
                                        </tr>
                                        </thead>
                                        <tbody>
                                        {
                                            productVariantPrices.map((productVariantPrice, index) => {
                                                return (
                                                    <tr key={index}>
                                                        <td>{productVariantPrice.title}</td>
                                                        <td><input className="form-control" type="text" name='price' id='price' onChange={(e) => onProductVariantPriceAndStockChange(e, productVariantPrice.title)} value={productVariantPrice.price}/></td>
                                                        <td><input className="form-control" type="text" name='stock' id='stock' onChange={(e) => onProductVariantPriceAndStockChange(e, productVariantPrice.title)} value={productVariantPrice.stock}/></td>
                                                    </tr>
                                                )
                                            })
                                        }
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <button type='button' onClick={saveProduct} className="btn btn-lg btn-primary">{props.is_for_update == "true" ? "Update" : "Save" }</button>
                <button type='button' className="btn btn-lg btn-secondary">Cancel</button>
                
            </section>
        </div>
    );
};

export default CreateProduct;
